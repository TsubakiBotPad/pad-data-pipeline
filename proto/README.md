Acquire protoc:

```
wget https://github.com/protocolbuffers/protobuf/releases/download/v3.10.1/protoc-3.10.1-linux-x86_64.zip
unzip protoc-3.10.1-linux-x86_64.zip
```

Install the protoc plugin for dart:

```
flutter pub global activate protoc_plugin
```

You must have 3 items on your path now:
* protoc
* dart (this will be installed in your flutter/bin/cache/dart-sdk)
* your flutter pub bin (flutter/.pub-cache/bin)


To compile:

```
protoc -I=. --python_out=python/dadguide_proto --dart_out=dart/dadguide_proto enemy_skills.proto
```

Copy the dart files into the dadguide flutter project.
