CHARLIE Smart Connector for Chiminey
==================================
CHARLIE allows formal model checking of a system modeled as petri net.  'CHARLIE Smart Connector for Chiminey' allows payload parameter sweep over perti net models which facilitates scheduling computes over the cloud for parallel execution.

Once 'CHARLIE Smart Connector' is activated in Chiminey, Chiminey portal then allows to configure and submit a CHARLIE job for execution.

CHARLIE Smart Connector(SC) install
-----------------------------------
The CHARLIE SC needs to install CHARLIE binary. During activation of CHARLIE SC, the user is required to download appropriate version of charlie. However, since Charlie comes with GUI installer, please install Charlie in lnux environment and use the follwoing shell script to create 'charlie.tar.gz':
```
#!/bin/sh

if [ -d ./charlie ]; then
    rm -r ./charlie
fi

if [ -f ./charlie.tar.gz ]; then
    rm  ./charlie.tar.gz
fi

mkdir ./charlie

cp charlie.jar ./charlie/charlie.jar
cp ./tCharlie.sh ./charlie/tCharlie.sh
cp -r ./externalpackages ./charlie/externalpackages

tar -zcvf charlie.tar.gz ./charlie

```
please place the 'charlie.tar.gz' file in the 'package' directory of chiminey install. Please refer to installation steps described in https://github.com/alahmedabdullah/charlieconnector/blob/master/SETUP.md file.

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
'bootstrap.sh' installs all dependencies required to prepeare job execution environment for CHARLIE. Please note that CHARLIE is installed in '/opt' directory. Following is the content of 'bootstrap.sh' for CHARLIE SC:    

```
#!/bin/sh
# version 2.0

WORK_DIR=`pwd`

CHARLIE_PACKAGE_NAME=$(sed 's/CHARLIE_PACKAGE_NAME=//' $WORK_DIR/package_metadata.txt)
mv $WORK_DIR/$CHARLIE_PACKAGE_NAME /opt
cd /opt

# how to get the latest oracle java version ref: https://gist.github.com/n0ts/40dd9bd45578556f93e7
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

The 'main.sh' is a simple script that executes a shell script 'run.sh'. Following is the content of 'main.sh' for CHARLIE SC:

```
#!/bin/sh

INPUT_DIR=$1
cp run.sh_template $INPUT_DIR/run.sh_template

cd $INPUT_DIR
sh ./run.sh $@

# --- EOF ---
```
Following is the content of 'run.sh' that executes a given CHARLIE job :

```
#!/bin/sh

INPUT_DIR=$1
OUTPUT_DIR=$2

java_exe=$(whereis java 2>&1 | awk '/java/ {print $2}')
java_path=$(dirname $java_exe)

export PATH=$java_path:$PATH

/opt/charlie/tCharlie.sh $(cat cli_parameters.txt) &> runlog.txt

cp ./*.txt ../$OUTPUT_DIR
```

The Input Directory
-------------------
A connector in Chiminey system specifes a 'Input Location' through 'Create Job' tab of the Chimney-Portal. Files located in the 'Input Location' directory is loaded to each VM for cloud execution. The content of 'Input Location' may vary for different runs. Chiminey allows parameteisation of the input envrionment. Any file with '_template' suffix located in the input directory is regarded as template file. Chiminey internally replaces values of the template tags based on the 'payload parameter sweep' provied as Json Dictionary from 'Create Job' tab in the Chiminey portal.


The input directory is provided with a default template file 'cli_parameters.txt_template' which is availabe in 'input_charlie' directory of CHARLIE SC install. All the template tags specified in  the cli_parameters.txt_template file will be internally replaced by Chiminey with corresponding values that are passed in from 'Chiminey Portal' as Json dictionary. The 'cli_parameters.txt_template' is  also renamed to 'cli_parameters.txt' with all template tags replaced with corresponding values.

For example let us assume following shell command is used to execute a CHARLIE model 'test.andl':

```
tCharlie.sh --netfile=test.andl --analyze=pinv --converge=1 --exportFile=result.txt
```
So value for 'Payload parameter sweep' field has to be a JSON dictionary passed in from Chiminey-Portal's 'Create Job' tab:

```
{ "cli_parameters" :  [ "--netfile=test.andl --analyze=pinv --converge=1 --exportFile=result.txt" ] }

```
Note that the {{cli_parameters}} is the tag name defined in the 'cli_parameters.txt_template' and is replaced by appropiate value passed in through JSON dictionary.


Configure, Create and Execute a CHARLIE Job
------------------------------------------
'Create Job' tab in 'Chiminey Portal' lists 'sweep_charlie' form for creation and submission of charlie job. 'sweep_charlie' form require definition of 'Compute Resource Name' and 'Storage Location'. Appropiate 'Compute Resource' and 'Storage Resource' need to be defined  through 'Settings' tab in the 'Chiminey portal'.

Payload Parameter Sweep
-----------------------
Payload parameter sweep for 'CHARLIE Smart Connector' in Chiminey System may be performed by specifying appropiate JSON dictionary in 'Payload parameter sweep' field  of the 'sweep_charlie' form. An example JSON dictionary to run internal sweep for the 'test.andl' could be as following:

```
{"cli_parameters" :  [ "--netfile=test.andl --analyze=pinv --converge=1 --exportFile=result.txt", "--netfile=test.andl --analyze=tinv --deleteTrivial=1 enableMCSC=1  --exportFile=result.txt", "--netfile=test.andl --analyze=pinv --deleteTrivial=1 enableMCSC=1  --exportFile=result.txt" ] }
``` 
Above would create three individual process. To allocate maximum two cloud VMs - thus execute two CHARLIE job in the same VM,  input fields in 'Cloud Compute Resource' for 'sweep_charlie' form has to be:

```
Number of VM instances : 2
Minimum No. VMs : 1
```
