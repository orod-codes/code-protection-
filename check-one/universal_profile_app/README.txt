Universal User Profile + BMI — same architecture in every language:

  Models   → user record (name, age, weight kg, height cm)
  Services → BMI = weight / (height_m²)
  Utils    → CLI prompts
  Main     → wires everything

Folders:

  python/   java/   node/   cpp/   csharp/   php/

Run examples (from each language folder unless noted):

  Python
    cd python && python3 main.py

  Java (from java/)
    javac -d out src/model/User.java src/service/BMIService.java \
      src/util/InputUtil.java src/Main.java
    java -cp out Main

  Node.js
    cd node && node main.js

  C++
    cd cpp && g++ -std=c++17 -o app main.cpp && ./app

  C# (Mono)
    cd csharp && mcs -out:app.exe Models/User.cs Services/BMIService.cs \
      Utils/ConsoleUtil.cs Program.cs && mono app.exe

  PHP (CLI; readline)
    cd php && php index.php

Protect the whole tree for customer delivery:

  cd "/path/to/check-one"
  python3 engine.py universal_profile_app --generate-folder universal_profile_app_customer

After injection, C/C++ customer builds may need -lcrypto if your engine adds OpenSSL guards.

C++ note: the runtime guard hashes main .cpp plus every .h / .hpp / .hh / .hxx in the SAME folder
as that .cpp (listed on // __EI_HDRS__: in the guard). Changing a header without re-injecting
will fail verification. Legacy .cpp files without __EI_HDRS__ still hash only that .cpp.
