#!/bin/bash

if [ -z "$1" ] || [ -z "$2"] || [ -z "$3"] ; then
  echo "Please provide a FILE NAME as the first argument, CUIT as the second one and COMPANY NAME as a third one"
  exit 1
fi

nombre_key="$1"
cuit="$2"
nombre_empresa="$3"

# Create the folder
mkdir "$nombre_empresa"

csr_file="$nombre_empresa/$nombre_key.key"
cert_file="$nombre_empresa/$nombre_key.csr"

# Generate a private key
openssl genrsa -out "$csr_file" 2048

# Generate a CSR
openssl req -new -key "$csr_file" -subj "/C=AR/O=$nombre_empresa/CN=$nombre_empresa/serialNumber=CUIT $cuit"  -out "$cert_file"

