// =============================================================================
// Lap Sim Vehicle Construction
//
// Suspension topology defined as GenericWheeledSuspension via JSON:
//   Front: lap_sim/suspension/GenericDW_Front.json  (steerable double wishbone)
//   Rear:  lap_sim/suspension/GenericDW_Rear.json   (non-steerable double wishbone)
//
// Tires: Hoosier LC0 16x7.5-10 loaded directly from the .tir file via the
//        HoosierTire subclass defined below.
//
// All vehicle JSON files live under:
//   /home/fubc/chrono/build/data/vehicle/lap_sim/
// =============================================================================

#include <string>

#include "chrono/physics/ChSystemNSC.h"

#include "chrono_vehicle/ChVehicleModelData.h"
#include "chrono_vehicle/wheeled_vehicle/vehicle/WheeledVehicle.h"
#include "chrono_vehicle/wheeled_vehicle/tire/ChPac02Tire.h"

using namespace chrono;
using namespace chrono::vehicle;

// =============================================================================
// Hoosier LC0 16x7.5-10 tire
//
// MF parameters are loaded directly from the .tir file.  Mass and inertia are
// estimated from the tyre geometry (r = 0.207 m, m = 3.18 kg, w = 0.175 m)
// using a solid-cylinder approximation:
//   Iy  = 0.5 * m * r^2         ~= 0.068 kg·m²  (spin axis)
//   Ix  = Iz = 0.25 * m * r^2  ~= 0.034 kg·m²
// =============================================================================
class HoosierTire : public ChPac02Tire {
  public:
    explicit HoosierTire(const std::string& name) : ChPac02Tire(name) {}

    virtual double     GetTireMass()    const override { return 3.18; }
    virtual ChVector3d GetTireInertia() const override { return {0.034, 0.068, 0.034}; }

  protected:
    // Called by ChPac02Tire::Initialize(); loads all Magic Formula coefficients.
    virtual void SetMFParams() override {
        SetMFParamsByFile(
            std::string(LAP_SIM_DATA_DIR) +
            "tir/43070 Hoosier LC0 16x7.5-10 RIM 7 10 PSI.tir"
        );
    }
};

// =============================================================================

// Returns a fully initialised WheeledVehicle placed at init_pos.
std::shared_ptr<WheeledVehicle> build_vehicle(ChSystemNSC& system, const ChCoordsys<>& init_pos) {
    // Resolve all vehicle JSON "Input File" paths relative to the lap_sim data dir.
    vehicle::SetDataPath(std::string(LAP_SIM_DATA_DIR) + "vehicle/");

    auto vehicle = chrono_types::make_shared<WheeledVehicle>(
        &system,
        vehicle::GetDataFile("LapSimVehicle.json"),
        /*create_powertrain=*/true,
        /*create_tires=*/false
    );

    vehicle->Initialize(init_pos);

    for (auto& axle : vehicle->GetAxles()) {
        for (auto& wheel : axle->GetWheels()) {
            auto tire = chrono_types::make_shared<HoosierTire>("HoosierLC0");
            vehicle->InitializeTire(tire, wheel, VisualizationType::PRIMITIVES);
        }
    }

    return vehicle;
}