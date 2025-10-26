# 🏎️ Project Chrono FSAE Simulation Environment

## 📘 Overview
This project uses **Project Chrono (C++)** to model and simulate a Formula SAE race car with a custom suspension and **OpenCRG-based terrain**.  
The environment runs entirely inside a **Docker container on WSL2**, ensuring consistent builds and portability across systems (including HPC).

---

## ⚙️ System Configuration
- **Host OS:** Windows 11  
- **Backend:** WSL2 (Linux kernel 6.6)  
- **Container Engine:** Docker Desktop (Linux/WSL2 mode enabled)  
- **Chrono Base Image:** `uwsbel/projectchrono:8.0`  
  - Includes Chrono built from source  
  - Supports C++ development (no Python bindings)  
- **Current Status:** Docker container verified to run and compile C++ Chrono programs successfully  

---

## 📂 Project Structure
~/chrono_fsae/
├─ src/
│ └─ main.cpp # Entry point for simulation
├─ CMakeLists.txt # Links Chrono::ChronoEngine + Chrono::ChronoVehicle
├─ roads/ # Contains .crg road surface files (mounted read-only)
├─ configs/ # Vehicle and simulation parameter files
├─ out/ # Logs, CSVs, or other simulation outputs
└─ docker-compose.yml # Optional one-command build/run setup

yaml
Copy code

---

## 🚀 Current Workflow

### **1️⃣ Run Chrono container**
```bash
docker run --rm -it -v "$PWD":/work uwsbel/projectchrono:8.0 /bin/bash
2️⃣ Build and run your simulation
Inside the container:

bash
Copy code
cd /work
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DChrono_DIR=/opt/chrono/build
cmake --build . -j
./fsae_sim /work/roads/sample.crg
🧱 CMake Setup
cmake
Copy code
cmake_minimum_required(VERSION 3.16)
project(fsae_chrono CXX)

find_package(Chrono REQUIRED COMPONENTS ChronoEngine ChronoVehicle)

add_executable(fsae_sim src/main.cpp)
target_link_libraries(fsae_sim PRIVATE Chrono::ChronoEngine Chrono::ChronoVehicle)
target_compile_features(fsae_sim PRIVATE cxx_std_17)
🧩 main.cpp (example)
cpp
Copy code
#include <chrono/physics/ChSystemNSC.h>
#include <chrono_vehicle/terrain/CRGTerrain.h>
#include <iostream>

int main(int argc, char** argv) {
    std::cout << "Chrono version: " << CHRONO_VERSION << "\n";
    chrono::ChSystemNSC sys;

    if (argc > 1) {
        try {
            chrono::vehicle::CRGTerrain crg(argv[1]);
            std::cout << "Loaded CRG: " << argv[1] << "\n";
            std::cout << "Height at (0,0): " << crg.GetSurfaceHeight(0.0, 0.0) << " m\n";
        } catch (const std::exception& e) {
            std::cerr << "CRG load failed: " << e.what() << "\n";
        }
    } else {
        std::cout << "No CRG path given; skipping terrain init.\n";
    }

    return 0;
}
🧭 Next Steps
✅ Confirm OpenCRG support — if not enabled, rebuild Chrono from source inside a custom Dockerfile:

bash
Copy code
-DENABLE_MODULE_VEHICLE=ON -DENABLE_OPENCRG=ON
🚀 Add custom FSAE suspension, steering, and chassis modules

🧩 Add logging/telemetry outputs to /work/out/

☁️ Deploy same container image on HPC via Apptainer/Singularity for scaled runs

🎯 Long-Term Goals
Use this Dockerized environment as a reproducible base for:

Vehicle dynamics tuning and parameter sweeps

Terrain interaction (CRG surfaces)

Visualization (Irrlicht/VNC or headless mode)

CI/HPC batch simulations using the same build
