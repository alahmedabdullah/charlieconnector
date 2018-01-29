CHARLIE Smart Connector for Chiminey
==================================
CHARLIE allows formal model checking of a system modeled as petri net. 

Verifying a complex charlie model may become compute-intensive - thus make it a suitable candidate for parallel execution utilising compute resources over the cloud using Chiminey. "CHARLIE Smart Connector for Chiminey" allows payload parameter sweep over charlie perti net models which facilitates scheduling computes over the cloud for parallel execution.

Once "CHARLIE Smart Connector" is activated in Chiminey, Chiminey portal then allows to configure and submit a CHARLIE job for execution.

CHARLIE Smart Connector(SC) Core Function
-----------------------------------
A payload (http://chiminey.readthedocs.io/en/latest/payload.html#payload) provides the core functionality of CHARLIE SC. The payload structure of CHARLIE SC is as following:

```
payload_charlie/
|--- bootstrap.sh
|--- process_payload
|    |---main.sh
     |---run.sh_template
```
The CHARLIE SC needs to install CHARLIE binary. During activation of CHARLIE SC, the user is required to download appropriate version of charlie and place in the 'package' directory of Chiminey install. Please refer to installation steps described in https://github.com/alahmedabdullah/charlieconnector/blob/master/SETUP.md file.

"bootstrap.sh" installs all dependencies required to prepeare job execution environment for CHARLIE. Please note that CHARLIE is installed in "/opt" directory. Following is the content of "bootstrap.sh" for CHARLIE SC:    

```
#!/bin/sh
# version 2.0

WORK_DIR=`pwd`

CHARLIE_PACKAGE_NAME=$(sed 's/CHARLIE_PACKAGE_NAME=//' $WORK_DIR/package_metadata.txt)
mv $WORK_DIR/$CHARLIE_PACKAGE_NAME /opt
cd /opt

# how to get the latest oracle java version ref: https://gist.github.com/n0ts/40dd9bd45578556f93e7
cd /opt/

ext="tar.gz"
jdk_version=8

readonly url="http://www.oracle.com"

readonly jdk_download_url1="$url/technetwork/java/javase/downloads/index.html"

#echo dlurl1=$jdk_download_url1

readonly jdk_download_url2=$(
    curl -s $jdk_download_url1 | \
    egrep -o "\/technetwork\/java/\javase\/downloads\/jdk${jdk_version}-downloads-.+?\.html" | \
    head -1 | cut -d '"' -f 1
)

#echo dlurl2=$jdk_download_url2

[[ -z "$jdk_download_url2" ]] && echo "Could not get jdk download url - $jdk_download_url1" >> /dev/stderr

readonly jdk_download_url3="${url}${jdk_download_url2}"

#echo dlurl3=$jdk_download_url3

readonly jdk_download_url4=$(curl -s $jdk_download_url3 | egrep -o "http\:\/\/download.oracle\.com\/otn-pub\/java\/jdk\/[7-8]u[0-9]+\-(.*)+\/jdk-[7-8]u[0-9]+(.*)linux-x64.$ext")

#echo dlurl4=$jdk_download_url4

for dl_url in ${jdk_download_url4[@]}; do
    wget --no-cookies \
         --no-check-certificate \
         --header "Cookie: oraclelicense=accept-securebackup-cookie" \
         -N $dl_url
done

JAVA_TARBALL=$(basename $dl_url)
tar xzfv $JAVA_TARBALL


java_exe=$(whereis java 2>&1 | awk '/java/ {print $2}')
java_path=$(dirname $java_exe)

echo $java_exe $java_path
export PATH=$java_path:$PATH

tar -zxvf $CHARLIE_PACKAGE_NAME
cd $WORK_DIR
```

The "main.sh" is a simple script that executes a shell script "run.sh" which must be already available in INPUT_DIR. It also passes on commmand line arguments i.e. INPUT_DIR and OUTPUT_DIR to "run.sh". The INPUT_DIR is passed in to "main.sh", where CHARLIE model files are loaded. Following is the content of "main.sh" for CHARLIE SC:

```
#!/bin/sh

INPUT_DIR=$1
cp run.sh_template $INPUT_DIR/run.sh_template

cd $INPUT_DIR
sh ./run.sh $@

# --- EOF ---
```
The "main.sh" executes "run.sh" which internally generated file based on "run.sh_template". The template filename must have "_template" suffix and need to be placed in the "Input Location" which is specified in "Create Job" tab of the Chiminey-Portal. Following is the content of "run.sh_template" that executes a given CHARLIE job :

```
#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

java_exe=$(whereis java 2>&1 | awk '/java/ {print $2}')
java_path=$(dirname $java_exe)

export PATH=$java_path:$PATH


/opt/charlie/tCharlie.sh {{cli_parammeters}} >> $OUTPUT_DIR/run.log
```
All the template tags specified in  the run.sh_template file will be internally replaced by Chiminey with corresponding values that are passed in from "Chiminey Portal" as Json dictionary. This "runs.sh_template" is  also renamed to "run.sh" with all template tags replaced with corresponding values. 

For example let us assume following shell command is used to execute a CHARLIE model "test.andl":

```
/opt/charlie/tCharlie.sh --netfile=test.andl --analyze=pinv --converge=1 --exportFile=result.txt
```  
So the "Payload parameter sweep", which is a JSON dictionary to be passed in from Chiminey-Portal's "Create Job" tab:

```
{ "cli_parameters" :  [ "--netfile=test.andl --analyze=pinv --converge=1 --exportFile=result.txt" ] }

```
Note that the "cli_parameters" is the tag name defined in the run.sh_template and will be replaced by appropiate value passed in through JSON dictionary .

The Input Directory
-------------------
A connector in Chiminey system specifes a "Input Location" through "Create Job" tab of the Chimney-Portal. Files located in the "Input Location" directory is loaded to each VM for cloud execution. The content of "Input Location" may vary for different runs. Chiminey allows parameteisation of the input envrionment. Any file with "_template" suffix located in the input directory is regarded as template file. Chiminey internally replaces values of the template tags based on the "payload parameter sweep" provied as Json Dictionary from "Create Job" tab in the Chiminey portal.

Configure, Create and Execute a CHARLIE Job
------------------------------------------
"Create Job" tab in "Chiminey Portal" lists "sweep_charlie" form for creation and submission of charlie job. "sweep_charlie" form require definition of "Compute Resource Name" and "Storage Location". Appropiate "Compute Resource" and "Storage Resource" need to be defined  through "Settings" tab in the "Chiminey portal".

Payload Parameter Sweep
-----------------------
Payload parameter sweep for "CHARLIE Smart Connector" in Chiminey System may be performed by specifying appropiate JSON dictionary in "Payload parameter sweep" field  of the "sweep_charlie" form. An example JSON dictionary to run internal sweep for the "train.tpn" could be as following:

```
{ n" ], "param_string" :  [ "-R -TPN -v -tc", "-C -TPN -v -tc", "-V -TPN -v -tc"] }
{"cli_parameters" :  [ "--netfile=test.andl --analyze=pinv --converge=1 --exportFile=result.txt", "--netfile=test.andl --analyze=tinv --deleteTrivial=1 enableMCSC=1  --exportFile=result.txt", "--netfile=test.andl --analyze=pinv --deleteTrivial=1 enableMCSC=1  --exportFile=result.txt" ] }
``` 
Above would create three individual process. To allocate maximum two cloud VMs - thus execute two CHARLIE job in the same VM,  input fields in "Cloud Compute Resource" for "sweep_charlie" form has to be:

```
Number of VM instances : 2
Minimum No. VMs : 1
```
