#!bin/bash

export PATH=$PATH:$(pwd)
set -x 
declare -a BUILDLIST=(
python-indico-plugins-mpp:0.1
)
#mkdir -p python-indico/3.3.0/rpmbuild/RPMS/noarch
#touch python-indico/3.3.0/rpmbuild/RPMS/noarch/1.rpm
#exit 0
#declare -a BUILDLIST=(
#python-pypdf:4.0.1
#python-indico-mpp-configuration:3.3
#python-iso4217:1.11.20220401
#python-indico:3.3.0
#)
for a in "${BUILDLIST[@]}" 
do
p=$(echo $a | cut -f1 -d: )
v=$(echo $a | cut -f2 -d: )
mkdir -p  logs
(sh srpmsbuild.sh $p $v --build &> logs/$p$v".log"  && sleep 2 && yum -y install ./$p/$v/rpmbuild/RPMS/*/*.rpm  )  || cat logs/$p$v".log"
#&> logs/$p$v".log" || echo "$p $v build failed" 
done
wait
exit
