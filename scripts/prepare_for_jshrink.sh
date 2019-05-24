#!/bin/bash

#Full path please
app_jar=$1
lib_jar=$2
test_jar=$3
src_dir=$4
new_maven_dir=$5

mkdir "${new_maven_dir}"

echo "<project xmlns=\"http://maven.apache.org/POM/4.0.0\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"" >"${new_maven_dir}/pom.xml"
echo "         xsi:schemaLocation=\"http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd\">" >>"${new_maven_dir}/pom.xml"
echo "        <modelVersion>4.0.0</modelVersion>" >>"${new_maven_dir}/pom.xml"                             
echo "        <groupId>edu.ucla.cs</groupId>" >>"${new_maven_dir}/pom.xml"                                 
echo "        <artifactId>maven-package</artifactId>" >>"${new_maven_dir}/pom.xml"                         
echo "        <version>1.0-SNAPSHOT</version>" >>"${new_maven_dir}/pom.xml"                                
echo "        <packaging>jar</packaging>" >>"${new_maven_dir}/pom.xml"                                     
echo "        <dependencies>" >>"${new_maven_dir}/pom.xml"                                                 
echo "                <dependency>" >>"${new_maven_dir}/pom.xml"                                           
echo "                        <groupId>edu.ucla.cs</groupId>" >>"${new_maven_dir}/pom.xml"                 
echo "                        <artifactId>libraries</artifactId>" >>"${new_maven_dir}/pom.xml"             
echo "                        <version>1.0-SNAPSHOT</version>" >>"${new_maven_dir}/pom.xml"                
echo "                        <scope>system</scope>" >>"${new_maven_dir}/pom.xml"                          
echo "                        <systemPath>\${project.basedir}/$(basename ${lib_jar})</systemPath>" >>"${new_maven_dir}/pom.xml"
echo "                </dependency>" >>"${new_maven_dir}/pom.xml"                                          
echo "			<dependency>" >>"${new_maven_dir}/pom.xml"
echo "				<groupId>junit</groupId>" >>"${new_maven_dir}/pom.xml"
echo "				<artifactId>junit</artifactId>" >>"${new_maven_dir}/pom.xml"
echo "				<version>4.12</version>" >>"${new_maven_dir}/pom.xml"
echo "				<scope>test</scope>" >>"${new_maven_dir}/pom.xml"
echo "				</dependency>" >>"${new_maven_dir}/pom.xml"
echo "        </dependencies>" >>"${new_maven_dir}/pom.xml" 
echo "        <properties>" >>"${new_maven_dir}/pom.xml"                                                   
echo "                <maven.compiler.source>1.8</maven.compiler.source>" >>"${new_maven_dir}/pom.xml"      
echo "                <maven.compiler.target>1.8</maven.compiler.target>" >>"${new_maven_dir}/pom.xml"     
echo "        </properties>" >>"${new_maven_dir}/pom.xml"                                                  
echo "</project>" >>"${new_maven_dir}/pom.xml"

mkdir "${new_maven_dir}/target"
mkdir "${new_maven_dir}/target/classes"
mkdir "${new_maven_dir}/target/test-classes"

{
	unzip "${app_jar}" -d"${new_maven_dir}/target/classes/"
	unzip "${test_jar}" -d"${new_maven_dir}/target/test-classes/"
	rm -rf "${new_maven_dir}/target/test-classes/org/junit" "${new_maven_dir}/target/test-classes/org/hamcrest"
} &>/dev/null


rm -rf "${new_maven_dir}/target/test-classes/junit"
if [ -d "${src_dir}" ]; then
	cp -r "${src_dir}" "${new_maven_dir}/"
else
	mkdir "${new_maven_dir}/src"
fi
cp "${lib_jar}" "${new_maven_dir}/"

