Acquire protoc: (Note: if you have snap installed, sudo snap install protoc --classic)

```
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.10.1/protoc-3.10.1-linux-x86_64.zip
unzip protoc-3.10.1-linux-x86_64.zip
```

Install the protoc plugin for dart: (NOTE: You can skip to compiling if only working on the pipeline)

```
flutter pub global activate protoc_plugin
```

You must have 3 items on your path now:
* protoc
* dart (this will be installed in your flutter/bin/cache/dart-sdk)
* your flutter pub bin (flutter/.pub-cache/bin)


To compile:

```
protoc -I=. --python_out=../etl/dadguide_proto enemy_skills.proto
# Change this path to match your installation
protoc -I=. --dart_out=../../../AndroidStudioProjects/dadguide2/lib/proto/enemy_skills/ enemy_skills.proto
```
