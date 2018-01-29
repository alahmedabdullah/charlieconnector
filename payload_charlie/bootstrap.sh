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
