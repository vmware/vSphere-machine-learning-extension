+++
title = "Testbed Setup"
description = "Set up vSphere with Tanzu on single host"
weight = 15
+++

### Prerequisites
---

1.  A dedicated physical machine that can run ESXi 8.0.
    1.  Memory requirements: 64GB minimum, 128GB or more is recommended.
    2.  Disk space requirements: 1TB minimum, 2TB or more is recommended.
2.  A network segment that meets the following requirements:
    1.  At least a /24 segment with 200+ available IPs, with at least 20 static IPs and the rest are DHCP IPs.
    2.  DHCP, DNS, and NTP services are available in the network segment.
3.  ESXi 8.0 and vCenter Server 8.0 installer ISO files. The latest release of ESXi 8.0 and vCenter Server 8.0 are recommended.
4.  A Linux machine that can run docker commands if you have no control over the DNS server in the network segment.


### Steps to setup TKG demo environment
---

1. Fresh install ESXi 8.0 on the physical machine. Configure NTP server for the ESXi.

2. Install vCenter Server 8.0 on the physical machine. Please pay attention to the following points when running the installation wizard:

	1. Be sure to enable thin disk mode for vCenter Server if available disk space is less than 1.5TB.
	2. Be sure to configure NTP server.

3. Create a new datacenter in the vCenter Server, and then create a new cluster in the datacenter. Be sure to enable DRS for this new cluster (In this example, the name of the datacenter is **Demo**, and the name of the cluster is **Tanzu**).
4. Add the ESXi host installed in step 1 to the cluster created in step 3. Right click the host, and then click **Maintenance Mode** – **Exit Maintenance Mode**.
5. Right click the cluster created in step 3, and then click **New Resource Pool …** to create a new resource pool (In this example, the name of this resource pool is **TKG**).
6. Right click the datacenter created in step 3, and then click **New Folder** – **New VM and Template Folder …** to create a new VM folder (In this example, the name of this VM folder is **TKG**).
7. Click the ESXi host in Inventory view. Click **Configure** – **Networking** – **Virtual switches** – **ADD NETWORKING**. Select **Virtual Machine Port Group for a Standard Switch**. Set a name for this port group (In this example, the name of this port group is **tkg-network**).
8. Navigate to **Menu** – **Content Libraries**. Click **CREATE** link. Give a name to the content library (In this example, the name of this content library is **TKG Demo**). Use default settings for **2 Configure content library** and **3 Apply security policy**. Select the datastore on the ESXi machine in **4 Add storage**, and then finish this wizard.
9. Download the following TKG demo appliance files, and upload them to the content library created in step 8.

	1. Download [https://download3.vmware.com/software/vmw-tools/tkg-demo-appliance/TKG-Demo-Appliance-1.3.1.ova](https://download3.vmware.com/software/vmw-tools/tkg-demo-appliance/TKG-Demo-Appliance-1.3.1.ova). Click name of the content library created in step 8 (In this example, name of this content library is **TKG Demo**), and then click **ACTIONS** – **Import Item**. Click **Local file** – **UPLOAD FILES**, browse to file TKG-Demo-Appliance-1.3.1.ova, click **Open**. Click **IMPORT**.

	2. Download K8s v1.20.5 OVA from [https://customerconnect.vmware.com/downloads/details?downloadGroup=TKG-131&productId=988&rPId=53095](https://customerconnect.vmware.com/downloads/details?downloadGroup=TKG-131&productId=988&rPId=53095). Click **ACTIONS** – **Import Item**. Click **Local file** – **UPLOAD FILES**, browse to file photon-3-kube-v1.20.5+vmware.2-tkg.1-3176963957469777230.ova, click **Open**. Click **IMPORT**.

	3. Download K8s v1.19.9 OVA from [https://customerconnect.vmware.com/downloads/details?downloadGroup=TKG-131&productId=988&rPId=53095](https://customerconnect.vmware.com/downloads/details?downloadGroup=TKG-131&productId=988&rPId=53095). Click **ACTIONS** – **Import Item**. Click **Local file** – **UPLOAD FILES**, browse to file photon-3-kube-v1.19.9+vmware.2-tkg.1-11749392838678570289.ova, click **Open**. Click **IMPORT**.


10. Deploy K8s content library:

	1. Right click the **photon-3-kube-v1.20.5+vmware.2-tkg.1-3176963957469777230** item in content library, select **New VM from This Template …**. Name this VM as **photon-3-kube-v1.20.5_vmware.2**, select the VM folder created in step 6, select the resource pool created in step 5 in the next page, review and accept the license, select a datastore, select the port group created in step 7 as the destination network to connect to, and click **FINISH**. After the deployment is done, right click VM **photon-3-kube-v1.20.5_vmware.2** and click **Template** – **Convert to Template**.

	2. Right click the **photon-3-kube-v1.19.9+vmware.2-tkg.1-11749392838678570289** item in content library, select **New VM from This Template …**. Name this VM as **photon-3-kube-v1.19.9_vmware.2**, select the VM folder created in step 6, select the resource pool created in step 5 in the next page, review and accept the license, select a datastore, select the port group created in step 7 as the destination network to connect to, and click **FINISH**. After the deployment is done, right click VM **photon-3-kube-v1.19.9_vmware.2** and click **Template** – **Convert to Template**.


11. Deploy TKG demo appliance:

	1. Right click the resource pool created in step 5 and select **New Virtual Machine…**.
	2. Select **Deploy from template** and choose **TKG-Demo-Appliance-1.3.1**.
	3. Name this VM and put it in the VM folder created in step 6.
	4. Select the resource pool created in step 5 as compute resource.
	5. Select a datastore for this VM.
	6. Select the port group created in step 7 as network.
	7. Fill in **Networking** and **OS Credentials** sections in **Customize template** page.
	8. Click **FINISH**.

12. Power on the TKG demo appliance VM. Wait for the initialization process finishes, and then login with username **root** and password set in step 11.7.

13. Run command `ssh-keygen`, and then run `cat /root/.ssh/id_rsa.pub` to display the SSH key on terminal. Keep this terminal window open for use later.

14. Run the following steps to add a DNS record for the TKG setup:

	1. Login the Linux machine/VM prepared for this task as root. Run command `systemctl stop systemd-resolved` to stop the build-in DNS service if it is running.
	2. Create file **~/Corefile** with the following content using a text editor (like **vi**):
	3. Create file **~/example.db** with the following content using a text editor (like **vi**):
	4. Run the following command to launch CoreDNS service: 
	   ```bash
	   docker run --restart=always --volume=`pwd`:/root/ -p 53:53/udp harbor-repo.vmware.com/dockerhub-proxy-cache/coredns/coredns -conf ~/Corefile
	   ```
	5. Run the following command from the terminal of TKG demo appliance to verify this DNS server is setup correctly: 
	   ```bash
	   dig @<IP address of the Linux machine> registry.rainpole.io
	   ```

15. Edit file **/etc/systemd/network/99-dhcp-en.network**, change the DNS server setting in this file to the correct DNS server, not this appliance itself. If you have launched your own DNS service in step 14, point DNS server to the Linux VM you are using in step 14. Run the following commands to apply this change.
    ```bash
	systemctl restart systemd-networkd
	systemctl restart systemd-resolved
	```

16. Edit file **vsphere-tkg-mgmt-template.yaml**. Make the following changes:
    
     1. In **vSphere configuration** section, change **VSPHERE_SERVER** to the IP of the vCenter Server.
     2. Change **VSPHERE_PASSWORD** to the password of vSphere administrator.
     3. Change **VSPHERE_USERNAME** to the username of vSphere administrator.
     4. Change **VSPHERE_DATACENTER** to the name of datacenter created in step 3.
	 5. Change the path in **VSPHERE_RESOURCE_POOL** to the actual path, which means the datacenter name and cluster name in the path should be changed.
	 6. Change the datacenter name and datastore name in **VSPHERE_DATASTORE**.
	 7. Change the datacenter name and VM folder name in **VSPHERE_FOLDER**.
	 8. Change **VSPHERE_NETWORK** to the name of port group created in step 7.
	 9. Change **VSPHERE_CONTROL_PLANE_ENDPOINT** to the static IP address of TKG management cluster.
	 10. Copy the content of file **/root/.ssh/id_rsa.pub** (available on screen in step 13) to **VSPHERE_SSH_AUTHORIZED_KEY**.
	 11. In **Node configuration** section, check the resource settings of TKG nodes, especially the disk size. Make changes if needed.

17. Edit file **vsphere-tkg-workload-1-template.yaml** and **vsphere-tkg-workload-2-template.yaml**. Make similar changes to the two files according to step 16.

18. Run the following command to create TKG management cluster: 
    ```bash
	tanzu management-cluster create -f vsphere-tkg-mgmt-template.yaml -v2
	```
	This command takes about five minutes. Output of this command is like the following:

19. Run the following command to create TKG workload cluster 1: 
    ```bash
	tanzu cluster create -f vsphere-tkg-workload-1-template.yaml
	```
	This command may take 10 to 15 minutes. Output of this command is like the following:

20. Run the following command to create TKG workload cluster 2: 
    ```bash
	tanzu cluster create -f vsphere-tkg-workload-2-template.yaml --tkr v1.19.9---vmware.2-tkg.1
	```
	This command may take 10 to 15 minutes. Output of this command is like the following:
