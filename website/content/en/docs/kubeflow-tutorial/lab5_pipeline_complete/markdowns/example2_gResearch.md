# Lab 7: Kubeflow Pipeline

### Install Kubeflow Pipeline Package


```python
!pip install kfp --upgrade --user --quiet
```


```python
# confirm the kfp sdk
! pip show kfp
```

## Example 2: G-Research Crypto Forecasting

In this example, we would build Kubeflow Pipeline directly from the ***notebook***, without using Docker to build images first.

*We assume you have already finished, or at least gone through, Example 1. If not, we recommend you to at least quickly go through Example 1, as the model in Example 1 is easier to understand and some concept explanations are discussed more in details.*

### About this Model

This model comes from Kaggle Competition. Over $40 billion worth of cryptocurrencies are traded every day. The objective of this task is to correctly forecast short term returns in 14 popular cryptocurrencies. [G-Research](https://www.gresearch.co.uk/) is Europe’s leading quantitative finance research firm, and partered with [Cambridge Spark](https://www.cambridgespark.com) for this Kaggle Competition.

The dataset this model would use contains information on historic trades for several cryptoassets, such as Bitcoin and Ethereum. Dataset would be downloaded from Kaggle.

More details about this model and dataset itself or Kaggle Competition can be found [here](https://www.kaggle.com/competitions/g-research-crypto-forecasting/overview).

### Import Packages


```python
!pip install --user --upgrade pip
```


```python
import kfp
import kfp.components as comp
import kfp.dsl as dsl
from kfp.components import OutputPath
from typing import NamedTuple
```

### Design Pipeline

Again, we design our pipeline component by component. We build our components this time as Python function-based components. The Kubeflow Pipelines SDK makes it easier to build lightweight Python function-based components by saving the effort of creating a component specification. Python function-based components make it easier to build pipeline components by building the component specification for you. Python function-based components also handle the complexity of passing inputs into your component and passing your function’s outputs back to your pipeline.

Let's walk through this concrete example to understand above ideas better.

Note that the overall workflow follows from original model itself. So please do not freak out when you see long, heavy code cells.

Basically, the following modifications were required to the original function.
- The import statements were moved inside of the function. Python function-based components require standalone Python functions. This means that any required import statements must be defined within the function, and any helper functions must be defined within the function. 
- The function’s arguments all include `data_path` which specifies the location for data storage, and also accessing. This lets Kubeflow Pipelines know the where to extract the data in zipped tar file into, where your function stores the processed data or model, and where to access it and use it as inputs for components.


#### Download Data

We start from data downloading. As specified at the beginning of this example, the datasets we would use come from Kaggle competition.

**Setup Kaggle**

To enable our pipeline to download datasets from Kaggle while running, you need to first do some setups on Kaggle.
1. Go to this [Kaggle](https://www.kaggle.com/). Login to your account, and register an account if you do not have one.
2. Click on your user profile picture, and go to "Account".
3. On your profile, Account section, scroll down and find "API" section. Click on "Create New API Token" button.
4. Wait for a short while, a file called `kaggle.json` should be downloaded on your local computer. Open that json file. The `api-key` and `username` are the ones we would need.
5. Keep your Kaggle account login. Go to [G-Research Crypto Forecasting Rules](https://www.kaggle.com/competitions/g-research-crypto-forecasting/rules), and click to accept those rules.

OK, you're all set! The above process is completely free so there is no need to worry. For now, you need to do above works to enable our pipeline to downaload data from Kaggle. In the future, we are planning to store those datasets somewhere that would be more convinient for your to downaload from.

And we are now ready for our Download Data component design.

Below is our Python-function-based Download Data component. It needs your Kaggle username and key. For convinience, you may directly copy and paste them. 

(But if you do not want them to be exposed directly to Kubeflow Pipeline, you may need to spend some time to create a Kubernetes secret to handle the sensitive API credentials. There are many, including the official one, [tutorials](https://kubernetes.io/docs/concepts/configuration/secret/) online, and we also provide you some sample codes in following cell. Detailed tutorial on this would come soon.)


```python
# download data step
# input dataset: name of dataset, need to be provided as input for pipeline
# input data_path: path for data storage, need to be provided as input for pipeline
# return: a print function, the printed contents would be reveal in logs.
def download_data(dataset, data_path):
        
    # install the necessary libraries
    # as each component would run as a container, you need to import these necessary libraries here inside this function-based component
    import os, sys, subprocess, zipfile, pickle;
    # again, as each component would run as a container, we use 'subprocess.run' here to run command lines while pipeline running
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, '-m', 'pip', 'install','pandas'])
    subprocess.run([sys.executable, '-m', 'pip', 'install','kaggle'])
    
    # import libraries
    import pandas as pd
    
    # you may directly copy and paste your Kaggle username and key here for convinience
    kaggle_user = 'YOUR_KAGGLE_USERNAME'
    kaggle_key = 'YOUR_KAGGLE_KEY'
    
    # or, spend some time setup kaggle environment for data download
    # with open('/secret/kaggle-secret/password', 'r') as file:
    #     kaggle_key = file.read().rstrip()
    # with open('/secret/kaggle-secret/username', 'r') as file:
    #     kaggle_user = file.read().rstrip()
        
    os.environ['KAGGLE_USERNAME'], os.environ['KAGGLE_KEY'] = kaggle_user, kaggle_key
    
    # create data_path directory
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    # download kaggle's g-research-crypto-forecasting data
    subprocess.run(["kaggle","competitions", "download", "-c", dataset])
    
    # extract 'train.csv' and 'asset_details.csv' in g-research-crypto-forecasting.zip to data_path
    with zipfile.ZipFile(f"{dataset}.zip","r") as zip_ref:
        zip_ref.extractall(data_path, members=['train.csv', 'asset_details.csv'])
    
    return(print('-- DATA DOWNLOADED --'))
```

#### Load Data


```python
# input data_path: path for data storage, need to be provided as input for pipeline
# return: a print function, the printed contents would be reveal in logs.
def load_data(data_path):
        
    # install the necessary libraries
    import os, sys, subprocess, pickle;
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, '-m', 'pip', 'install','pandas'])
    
    # import libraries
    import pandas as pd

    TRAIN_CSV = f'{data_path}/train.csv'
    ASSET_DETAILS_CSV = f'{data_path}/asset_details.csv'
    
    # read TRAIN_CSV and ASSET_DETAILS_CSV
    df_train = pd.read_csv(TRAIN_CSV)
    df_asset_details = pd.read_csv(ASSET_DETAILS_CSV).sort_values("Asset_ID")
    
    df_train['datetime'] = pd.to_datetime(df_train['timestamp'], unit='s')
    df_train = df_train[df_train['datetime'] >= '2020-01-01 00:00:00'].copy()
    
    # Save the df_train data as a pickle file to be used by the feature_engineering component.
    with open(f'{data_path}/df_train', 'wb') as f:
        pickle.dump(df_train, f)
        
    # Save the df_train data as a pickle file to be used by the merge_data component.
    with open(f'{data_path}/df_asset_details', 'wb') as g:
        pickle.dump(df_asset_details, g)

    
    return(print('-- DATA LOADED --'))
```

#### Feature Engineering
Codes for this step follows most from original model itself (so don't freak out when seeing this long cell).

One thing to note here is that this component needs to save the feature engineered data as a pickle file which would be used later by the modeling component. Similar to Example 1, to enable modeling component to access this feature engineered data, we simply need to store it in the data path.
```python
# save the feature engineered data as a pickle file to be used by the modeling component.
    with open(f'{data_path}/feature_df', 'wb') as f:
        pickle.dump(feature_df, f)
```


```python
# input data_path: path for data storage, need to be provided as input for pipeline
# return: a print function, the printed contents would be reveal in logs.
def feature_engineering(data_path):
    
    # install the necessary libraries
    import sys, subprocess;
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, '-m', 'pip', 'install','pandas'])
    subprocess.run([sys.executable, '-m', 'pip', 'install','tqdm'])
    subprocess.run([sys.executable, '-m', 'pip', 'install','talib-binary'])
    
    # import Library
    import os, pickle, time, talib, datetime;
    import numpy as np
    import pandas as pd
    from tqdm import tqdm

    # loading the df_train data
    with open(f'{data_path}/df_train', 'rb') as f:
        df_train = pickle.load(f)
    
    # creating technical indicators
    
    # Create a function to calculate the Relative Strength Index
    def RSI(df, n):
        return talib.RSI(df['Close'], n)
    
    # Create a function to calculate the Average True Range
    def ATR(df, n):
        return talib.ATR(df["High"], df.Low, df.Close, n)

    # Create a function to calculate the Double Exponential Moving Average (DEMA)
    def DEMA(data, time_period):
        #Calculate the Exponential Moving Average for some time_period (in days)
        EMA = data['Close'].ewm(span=time_period, adjust=False).mean()
        #Calculate the DEMA
        DEMA = 2*EMA - EMA.ewm(span=time_period, adjust=False).mean()
        return DEMA
    
    # Create a function to calculate the upper_shadow
    def upper_shadow(df):
        return df['High'] - np.maximum(df['Close'], df['Open'])
    
    # Create a function to calculate the lower_shadow
    def lower_shadow(df):
        return np.minimum(df['Close'], df['Open']) - df['Low']
    
    
    def get_features(df, asset_id, train=True):
        '''
        This function takes a dataframe with all asset data and return the lagged features for a single asset.

        df - Full dataframe with all assets included
        asset_id - integer from 0-13 inclusive to represent a cryptocurrency asset
        train - True - you are training your model
              - False - you are submitting your model via api
        '''
        # filter based on asset id
        df = df[df['Asset_ID']==asset_id]

        # sort based on time stamp
        df = df.sort_values('timestamp')

        if train == True:
            df_feat = df.copy()

            # define a train_flg column to split your data into train and validation
            totimestamp = lambda s: np.int32(time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple()))
            valid_window = [totimestamp("01/05/2021")]

            df_feat['train_flg'] = np.where(df_feat['timestamp']>=valid_window[0], 0,1)
            df_feat = df_feat[['timestamp','Asset_ID', 'High', 'Low', 'Open', 'Close', 'Volume','Target','train_flg']].copy()
        else:
            df = df.sort_values('row_id')
            df_feat = df[['Asset_ID', 'High', 'Low', 'Open', 'Close', 'Volume','row_id']].copy()

        for i in tqdm([30, 120, 240]):
            # Applyin technical indicators
            df_feat[f'RSI_{i}'] = RSI(df_feat, i)
            df_feat[f'ATR_{i}'] = ATR(df_feat, i)
            df_feat[f'DEMA_{i}'] = DEMA(df_feat, i)

        for i in tqdm([30, 120, 240]):
            # creating lag features
            df_feat[f'sma_{i}'] = df_feat['Close'].rolling(i).mean()/df_feat['Close'] -1
            df_feat[f'return_{i}'] = df_feat['Close']/df_feat['Close'].shift(i) -1

        # new features
        df_feat['HL'] = np.log(df_feat['High'] - df_feat['Low'])
        df_feat['OC'] = np.log(df_feat['Close'] - df_feat['Open'])
        
        # Applyin lower_shadow and upper_shadow indicators
        df_feat['lower_shadow'] = np.log(lower_shadow(df)) 
        df_feat['upper_shadow'] = np.log(upper_shadow(df))

        # replace inf with nan
        df_feat.replace([np.inf, -np.inf], np.nan, inplace=True)

        # datetime features
        df_feat['Date'] = pd.to_datetime(df_feat['timestamp'], unit='s')
        df_feat['Day'] = df_feat['Date'].dt.weekday.astype(np.int32)
        df_feat["dayofyear"] = df_feat['Date'].dt.dayofyear
        df_feat["weekofyear"] = df_feat['Date'].dt.weekofyear
        df_feat["season"] = ((df_feat['Date'].dt.month)%12 + 3)//3
        
        # drop features
        df_feat = df_feat.drop(['Open','Close','High','Low', 'Volume', 'Date'], axis=1)

        # fill nan values with 0
        df_feat = df_feat.fillna(0)

        return df_feat
    
    # create your features dataframe for each asset and concatenate
    feature_df = pd.DataFrame()
    for i in range(14):
        print(i)
        feature_df = pd.concat([feature_df,get_features(df_train,i,train=True)])
      
    # save the feature engineered data as a pickle file to be used by the modeling component.
    with open(f'{data_path}/feature_df', 'wb') as f:
        pickle.dump(feature_df, f)
    
    return(print('-- FEATURE ENGINEERING FINISHED --')) 
```

#### Merge Assets Features

This component needs to access the featured data generated in above Feature Engineering component. That data is stored in the data path we specified.
```python
with open(f'{data_path}/feature_df', 'rb') as f:
        feature_df = pickle.load(f)
```


```python
# input data_path: path for data storage, need to be provided as input for pipeline
# return: a print function, the printed contents would be reveal in logs.
def merge_assets_features(data_path):
    
    # install the necessary libraries
    import sys, subprocess;
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, '-m', 'pip', 'install','pandas'])
    
    # import Library
    import os, pickle;
    import pandas as pd

    #loading the feature_df data
    with open(f'{data_path}/feature_df', 'rb') as f:
        feature_df = pickle.load(f)
        
    #loading the df_asset_details data
    with open(f'{data_path}/df_asset_details', 'rb') as g:
        df_asset_details = pickle.load(g)
    
    # assign weight column feature dataframe
    feature_df = pd.merge(feature_df, df_asset_details[['Asset_ID','Weight']], how='left', on=['Asset_ID'])

    #Save the feature_df as a pickle file to be used by the modelling component.
    with open(f'{data_path}/merge_feature_df', 'wb') as h:
        pickle.dump(feature_df, h)
        
    return(print('-- ASSETS FEATURES MERGED --'))  
```

#### Modeling
Again, the overall logic comes completely from the original ML model. Things we need to note here, for our pipeline lab, is, again, the location of data storage.


```python
# input data_path: path for data storage, need to be provided as input for pipeline
# return: a print function, the printed contents would be reveal in logs.
def modeling(data_path):
    
    # install the necessary libraries
    import sys, subprocess;
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, '-m', 'pip', 'install','pandas'])
    subprocess.run([sys.executable, '-m', 'pip', 'install','lightgbm'])
    
    # import Library
    import os, pickle, joblib;
    import pandas as pd
    import numpy as np
    import lightgbm as lgb
    from lightgbm import LGBMRegressor

    #loading the new_feats data
    with open(f'{data_path}/merge_feature_df', 'rb') as f:
        feature_df = pickle.load(f)
        
    # define features for LGBM
    features = ['Asset_ID', 'RSI_30', 'ATR_30',
           'DEMA_30', 'RSI_120', 'ATR_120', 'DEMA_120', 'RSI_240', 'ATR_240',
           'DEMA_240', 'sma_30', 'return_30', 'sma_120', 'return_120', 'sma_240',
           'return_240', 'HL', 'OC', 'lower_shadow', 'upper_shadow', 'Day',
           'dayofyear', 'weekofyear', 'season']
    categoricals = ['Asset_ID']
    
    # define the evaluation metric
    def weighted_correlation(a, train_data):

        weights = train_data.add_w.values.flatten()
        b = train_data.get_label()


        w = np.ravel(weights)
        a = np.ravel(a)
        b = np.ravel(b)

        sum_w = np.sum(w)
        mean_a = np.sum(a * w) / sum_w
        mean_b = np.sum(b * w) / sum_w
        var_a = np.sum(w * np.square(a - mean_a)) / sum_w
        var_b = np.sum(w * np.square(b - mean_b)) / sum_w

        cov = np.sum((a * b * w)) / np.sum(w) - mean_a * mean_b
        corr = cov / np.sqrt(var_a * var_b)

        return 'eval_wcorr', corr, True
    
    # define train and validation weights and datasets
    weights_train = feature_df.query('train_flg == 1')[['Weight']]
    weights_test = feature_df.query('train_flg == 0')[['Weight']]

    train_dataset = lgb.Dataset(feature_df.query('train_flg == 1')[features], 
                                feature_df.query('train_flg == 1')['Target'].values, 
                                feature_name = features,
                               categorical_feature= categoricals)
    val_dataset = lgb.Dataset(feature_df.query('train_flg == 0')[features], 
                              feature_df.query('train_flg == 0')['Target'].values, 
                              feature_name = features,
                             categorical_feature= categoricals)
    # add weights
    train_dataset.add_w = weights_train
    val_dataset.add_w = weights_test
    
    # LGBM params
    evals_result = {}
    params = {'n_estimators': 1200,
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'max_depth': -1, 
            'learning_rate': 0.01,
            'seed': 2022,
            'verbose': -1,
            }

    # train LGBM
    model = lgb.train(params = params,
                      train_set = train_dataset, 
                      valid_sets = [val_dataset],
                      early_stopping_rounds=60,
                      verbose_eval = 30,
                      feval=weighted_correlation,
                      evals_result = evals_result 
                     )
    
    # saving model
    joblib.dump(model, f'{data_path}/lgb.jl')
        
    return(print('-- MODELED --'))
```

#### Evaluate
This component would return the evaluation metrics, which would be reveal in Input/Output, Output artifacts on Kubeflow UI after pipeline finishes running. More details on this would be discussed later in pipeline running section.


```python
# input data_path: path for data storage, need to be provided as input for pipeline
# input metric_path: path to store evaluation metric
# return the evaluation metrics, which would be reveal in Input/Output, Output artifacts
def evaluation_result(data_path, 
                metrics_path: OutputPath(str)) -> NamedTuple("EvaluationOutput", [("mlpipeline_metrics", "Metrics")]):
    
    # import Library
    import sys, subprocess;
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, '-m', 'pip', 'install','lightgbm'])
    import json;
    from collections import namedtuple
    import joblib
    import lightgbm as lgb
    from lightgbm import LGBMRegressor
    
    # load model
    model = joblib.load(f'{data_path}/lgb.jl')

    # model evaluation
    root_mean_squared_error = model.best_score.get('valid_0').get('rmse')
    weighted_correlation = model.best_score.get('valid_0').get('eval_wcorr')
    
    # create kubeflow metric metadata for UI    
    metrics = {
                'metrics': [
                    {'name': 'root-mean-squared-error',
                    'numberValue':  root_mean_squared_error,
                    'format': 'RAW'},
                    {'name': 'weighted-correlation',
                    'numberValue':  weighted_correlation,
                    'format': 'RAW'}
                            ]
              }
    

    with open(metrics_path, "w") as f:
        json.dump(metrics, f)

    output_tuple = namedtuple("EvaluationOutput", ["mlpipeline_metrics"])

    return output_tuple(json.dumps(metrics))
```

### Create Pipeline Components

In this example, we use `kfp.components.create_component_from_func` to return a factory function that we would use to create pipeline steps.


```python
download_op = comp.create_component_from_func(download_data,base_image="python:3.7.1")
load_op = comp.create_component_from_func(load_data,base_image="python:3.7.1")
merge_assets_features_op = comp.create_component_from_func(merge_assets_features,base_image="python:3.7.1")
feature_eng_op = comp.create_component_from_func(feature_engineering,base_image="python:3.7.1")
modeling_op = comp.create_component_from_func(modeling, base_image="python:3.7.1")
evaluation_op = comp.create_component_from_func(evaluation_result, base_image="python:3.7.1")
```

### Build Pipeline


```python
# define pipeline
@dsl.pipeline(name="g-research-crypto-forecasting-pipeline", 
              description="g-research-crypto-forecasting-pipeline")

# Define parameters to be fed into pipeline
def g_research_crypto_forecast_pipeline(
                             dataset: str, # name of dataset, zip
                             data_path: str # path for data storage, would be used through entire pipeline, all components
                            ):
    # Define volume to share data between components.
    vop = dsl.VolumeOp(
    name="create_data_volume",
    resource_name="data-volume", 
    size="16Gi", 
    modes=dsl.VOLUME_MODE_RWO)
    
    
    # Create download container, using ops we defined in above code cell
    download_container = download_op(dataset, data_path)\
                        .add_pvolumes({data_path: vop.volume}) # add pvolumes, and mount it to data_path for data sharing among steps
    # Create load container.
    load_container = load_op(data_path)\
                    .add_pvolumes({data_path: download_container.pvolume})
    # Create feature engineering container.
    feat_eng_container = feature_eng_op(data_path)\
                            .add_pvolumes({data_path: load_container.pvolume})
    # Create merge_assets_feat container.
    merge_assets_feat_container = merge_assets_features_op(data_path)\
                                 .add_pvolumes({data_path: feat_eng_container.pvolume})
    # Create modeling container.
    modeling_container = modeling_op(data_path)\
                        .add_pvolumes({data_path: merge_assets_feat_container.pvolume})
    # Create prediction container.
    evaluation_container = evaluation_op(data_path).add_pvolumes({data_path: modeling_container.pvolume})
```

Similar to Example 1, compile our difined pipeline into a YAML file.


```python
kfp.compiler.Compiler().compile(
    pipeline_func=g_research_crypto_forecast_pipeline,
    package_path='pipeline_gResearch.yaml')
```

You should then be able to see a file called `pipeline_gResearch.yaml` in your current directory.

### Run Pipeline

Again, we provide you with a compiled pipeline YAML file `gResearch_pipeline_test.yaml`. Feel free to use it.

Similar to Example 1, download `pipeline_gResearch.yaml`, and upload it to Pipelines on Kubeflow UI.

![g1](./img/g1.png)

![g2](./img/g2.png)

![g3](./img/g3.png)

This pipeline graph is more complex than the one in Example 1. You may take some time going through it. 

Again, create an experiment for this pipeline, and create a run. This time, you need to provide two inputs, `dataset` and `data_path`, exactly the ones for our first step Data Download. If you do not intend to make any personalization on datasets and data path, enter following values
```python
# arguments
# "" not needed while inputting them
dataset = "g-research-crypto-forecasting"
data_path = "/mnt"
```

![g4](./img/g4.png)

![g5](./img/g5.png)

The pipeline would start to run then. You would be able to see the running process in Runs Page on Kubeflow UI.

![g6](./img/g6.png)

The pipeline running may take some time, as the datasets is pretty big and there are much more steps in this example. There would be a green symbol appears next to each component after its completion. And you can always click on each component to see its details, such as its input/output, volumes, logs, and pod.

![g7](./img/g7.png)

After the whole pipeline finishes running, click on any of the component/step that you are interested in. You should be able to see main-logs under Input/Output, Output artifacts. 

Specifically, click on Evaluation Result Step, you should see "metrics" under Input/Output, Output artifacts. Click into them to see the evaluation metrics.

We also provide you with example logs of evaluation metrics in [logs](./logs/) folder.

## Troubleshooting
