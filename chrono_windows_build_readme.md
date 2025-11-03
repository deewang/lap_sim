# Project Chrono — Windows Build (VS2022)

**Goal:** Reproduce this setup: Chrono with **Vehicle + Irrlicht + OpenCRG**, configured via **CMake GUI**, dependencies from **vcpkg** (Irrlicht) and Chrono batch scripts (Eigen, OpenCRG, optional GL helpers).

**Tested On:** Windows 11 x64, Visual Studio 2022 (MSVC v143)

---

## Paths Used (customize as you wish)

- Chrono source: `C:\Users\<you>\chrono`
- Out-of-tree build: `C:\Users\<you>\chrono_build`
- Third-party deps: `C:\Users\<you>\ChronoDeps`
- vcpkg root: `C:\vcpkg`

---

## 0) Prerequisites (install once)

1. **Visual Studio 2022**
   - Workload: **Desktop development with C++**
   - Components: MSVC v143 toolset, CMake, Windows 10/11 SDK

2. **Git** – <https://git-scm.com>

3. **vcpkg**
   ```powershell
   git clone https://github.com/microsoft/vcpkg C:\vcpkg
   C:\vcpkg\bootstrap-vcpkg.bat
   ```

---

## 1) Get Chrono source

```powershell
git clone https://github.com/projectchrono/chrono C:\Users\<you>\chrono
```

Create working folders:

```powershell
mkdir C:\Users\<you>\chrono_build
mkdir C:\Users\<you>\ChronoDeps
```

---

## 2) Install dependencies

### 2.1 Eigen (via Chrono script)

```bat
cd C:\Users\<you>\chrono\contrib\build-scripts\windows
buildEigen.bat "C:\Users\<you>\ChronoDeps\eigen"
```

You should get:
```
C:\Users\<you>\ChronoDeps\eigen\
  include\eigen3\...
  share\eigen3\cmake\Eigen3Config.cmake
```

### 2.2 OpenCRG (via Chrono script)

```bat
cd C:\Users\<you>\chrono\contrib\build-scripts\windows
buildOpenCRG.bat "C:\Users\<you>\ChronoDeps\openCRG"
```

You should get:
```
C:\Users\<you>\ChronoDeps\openCRG\
  include\crgBaseLib.h ...
  lib\OpenCRG.lib
  lib\OpenCRG_d.lib
  lib\OpenCRG_rd.lib
  lib\OpenCRG_s.lib
```

### 2.3 GL helper libs (optional)

```bat
cd C:\Users\<you>\chrono\contrib\build-scripts\windows
buildGL.bat "C:\Users\<you>\ChronoDeps\gl"
```

(If GLEW complains about old CMake minimum version, you can skip it—**not required for Irrlicht demos**.)

### 2.4 Irrlicht (via vcpkg)

```powershell
C:\vcpkg\vcpkg install irrlicht:x64-windows
```

Key files:
```
C:\vcpkg\installed\x64-windows\include\irrlicht.h
C:\vcpkg\installed\x64-windows\lib\Irrlicht.lib
C:\vcpkg\installed\x64-windows\bin\Irrlicht.dll
C:\vcpkg\installed\x64-windows\share\irrlicht\...
```

---

## 3) Configure with CMake GUI

Open **CMake (cmake-gui)**

- **Where is the source code:** `C:\Users\<you>\chrono`
- **Where to build the binaries:** `C:\Users\<you>\chrono_build`
- Click **Configure** → *Visual Studio 17 2022* → *x64* → **Finish**

**Turn ON:**
- `BUILD_DEMOS`
- `CH_ENABLE_MODULE_VEHICLE`
- `CH_ENABLE_MODULE_IRRLICHT`
- `CH_ENABLE_OPENCRG`
- *(optional)* `CH_USE_EIGEN_OPENMP`
- Keep `CH_USE_MSVC_STATIC_RUNTIME` **OFF** (default)

**Set paths (Add Entry if missing):**

**Eigen**
- `Eigen3_DIR` → `C:\Users\<you>\ChronoDeps\eigen\share\eigen3\cmake`

**OpenCRG**
- `OpenCRG_INCLUDE_DIR` → `C:\Users\<you>\ChronoDeps\openCRG\include`
- `OpenCRG_LIBRARY`     → `C:\Users\<you>\ChronoDeps\openCRG\lib\OpenCRG.lib`
- *(optional)* `OpenCRG_DLL` → *(leave empty if static)*

**Irrlicht**
- `Irrlicht_ROOT`        → `C:\vcpkg\installed\x64-windows`
- `Irrlicht_DIR`         → `C:\vcpkg\installed\x64-windows\share\irrlicht`
- `Irrlicht_INCLUDE_DIR` → `C:\vcpkg\installed\x64-windows\include`
- `Irrlicht_LIBRARY`     → `C:\vcpkg\installed\x64-windows\lib\Irrlicht.lib`
- `Irrlicht_DLL`         → `C:\vcpkg\installed\x64-windows\bin\Irrlicht.dll`

Click **Configure** until no red entries remain → **Generate** → **Open Project**.

---

## 4) Build in Visual Studio

- Set **Solution Config** = **Release**, **x64**
- **Build → Build Solution** (use **Rebuild** after changing CMake options)

Artifacts:
```
C:\Users\<you>\chrono_build\bin\Release\*.exe
C:\Users\<you>\chrono_build\bin\data\...   (auto-copied)
```

---

## 5) Make `Irrlicht.dll` available at runtime

Choose **one**:

**A) Copy DLL into the output folder (simple)**
```powershell
copy C:\vcpkg\installed\x64-windows\bin\Irrlicht.dll C:\Users\<you>\chrono_build\bin\Release\ /Y
```

**B) Run with PATH set (terminal)**
```powershell
cd C:\Users\<you>\chrono_build\bin\Release
$env:PATH = "C:\vcpkg\installed\x64-windows\bin;$env:PATH"
.\demo_VEH_SuspensionTestRig.exe
```

**C) Permanent PATH** — add `C:\vcpkg\installed\x64-windows\bin` to your system **Path**.

*(Optional Visual Studio post-build event)*
```
xcopy "C:\vcpkg\installed\x64-windows\bin\Irrlicht.dll" "$(OutDir)" /Y
```

---

## 6) Run demos

From `C:\Users\<you>\chrono_build\bin\Release`:

```powershell
.\demo_VEH_SuspensionTestRig.exe
```

or

```powershell
.\demo_VEH_Test_FMTV_Ride.exe
```

Some demos prompt in the console (e.g., “Select vehicle: 1/2”) and then open an Irrlicht window.  
Warnings like “slow font initialization” are harmless.

---

## 7) Troubleshooting

- **`fatal error C1083: 'irrlicht.h' not found`**  
  → Fix `Irrlicht_INCLUDE_DIR` (`C:\vcpkg\installed\x64-windows\include`) and regenerate.

- **CMake says Irrlicht not found**  
  → Ensure all four are set: `Irrlicht_ROOT`, `Irrlicht_DIR`, `Irrlicht_INCLUDE_DIR`, `Irrlicht_LIBRARY`.

- **`Irrlicht.dll was not found` on launch**  
  → Copy DLL to `bin\Release` or add vcpkg `bin` to `PATH` (see §5).

- **OpenCRG not detected**  
  → Fill `OpenCRG_INCLUDE_DIR` and `OpenCRG_LIBRARY` exactly.

- **Do we need VSG/Vulkan?**  
  → No; we’re using **Irrlicht** renderer.

- **Static MSVC runtime?**  
  → Keep **OFF** unless you specifically need fully static CRTs.

---

## 8) Headless CMake (optional)

```powershell
cmake -S C:\Users\<you>\chrono -B C:\Users\<you>\chrono_build `
  -G "Visual Studio 17 2022" -A x64 `
  -DBUILD_DEMOS=ON `
  -DCH_ENABLE_MODULE_VEHICLE=ON `
  -DCH_ENABLE_MODULE_IRRLICHT=ON `
  -DCH_ENABLE_OPENCRG=ON `
  -DEigen3_DIR="C:/Users/<you>/ChronoDeps/eigen/share/eigen3/cmake" `
  -DOpenCRG_INCLUDE_DIR="C:/Users/<you>/ChronoDeps/openCRG/include" `
  -DOpenCRG_LIBRARY="C:/Users/<you>/ChronoDeps/openCRG/lib/OpenCRG.lib" `
  -DIrrlicht_ROOT="C:/vcpkg/installed/x64-windows" `
  -DIrrlicht_DIR="C:/vcpkg/installed/x64-windows/share/irrlicht" `
  -DIrrlicht_INCLUDE_DIR="C:/vcpkg/installed/x64-windows/include" `
  -DIrrlicht_LIBRARY="C:/vcpkg/installed/x64-windows/lib/Irrlicht.lib"

cmake --build C:\Users\<you>\chrono_build --config Release
copy C:\vcpkg\installed\x64-windows\bin\Irrlicht.dll C:\Users\<you>\chrono_build\bin\Release\ /Y
```

---

## 9) Share with teammates

- Zip and share:
  - `C:\Users\<you>\ChronoDeps\` (Eigen, OpenCRG, optional GL)
  - The Chrono commit used
  - This `README.md`
- They install VS2022 + vcpkg, then follow steps **2.4 → 6** pointing CMake to your `ChronoDeps`.

---

**Done! 🎉** You now have a repeatable Windows build of Project Chrono with Vehicle + Irrlicht + OpenCRG.
