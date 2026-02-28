#include <iostream>
#include <string>

#include "chrono/physics/ChSystemNSC.h"

#ifndef LAP_SIM_DATA_DIR
#define LAP_SIM_DATA_DIR "./"
#endif

#include "chrono_vehicle/ChVehicleModelData.h"
#include "chrono_vehicle/driver/ChPathFollowerDriver.h"
#include "chrono_vehicle/terrain/CRGTerrain.h"
#include "chrono_vehicle/wheeled_vehicle/vehicle/WheeledVehicle.h"
#include "chrono_vehicle/wheeled_vehicle/ChWheeledVehicleVisualSystemIrrlicht.h"

using namespace chrono;
using namespace chrono::vehicle;

std::shared_ptr<WheeledVehicle> build_vehicle(ChSystemNSC& system, const ChCoordsys<>& init_pos);

// =============================================================================

int main() {
    // -----------------------------------------------
    // System
    // -----------------------------------------------
    ChSystemNSC system;
    system.SetGravitationalAcceleration(ChVector3d(0, 0, -9.81));

    // -----------------------------------------------
    // Terrain  (must be created before the vehicle
    // so the start position is known)
    // -----------------------------------------------
    const std::string crg_file =
        std::string(LAP_SIM_DATA_DIR) + "tracks/crg/endurance2025.crg";

    CRGTerrain terrain(&system);
    terrain.UseMeshVisualization(true);
    terrain.SetContactFrictionCoefficient(0.8f);
    terrain.Initialize(crg_file);

    auto path          = terrain.GetRoadCenterLine();
    double road_width  = terrain.GetWidth();
    bool   path_closed = terrain.IsPathClosed();
    auto   init_csys   = terrain.GetStartPosition();
    init_csys.pos     += ChVector3d(0, 0, 0.5);  // 0.5 m above road surface

    std::cout << "Road length: " << terrain.GetLength() << " m\n";
    std::cout << "Road width:  " << road_width << " m\n";
    std::cout << "Closed loop: " << std::boolalpha << path_closed << "\n\n";

    // -----------------------------------------------
    // Vehicle
    // -----------------------------------------------
    auto vehicle = build_vehicle(system, init_csys);

    vehicle->SetChassisVisualizationType(VisualizationType::PRIMITIVES);
    vehicle->SetSuspensionVisualizationType(VisualizationType::PRIMITIVES);
    vehicle->SetSteeringVisualizationType(VisualizationType::PRIMITIVES);
    vehicle->SetWheelVisualizationType(VisualizationType::PRIMITIVES);

    // -----------------------------------------------
    // Driver — PID path follower
    // -----------------------------------------------
    const double target_speed = 10.0;  // m/s (~36 km/h)

    auto driver = chrono_types::make_shared<ChPathFollowerDriver>(
        *vehicle, path, "track_centerline", target_speed);
    driver->GetSteeringController().SetLookAheadDistance(5.0);
    driver->GetSteeringController().SetGains(0.5, 0.0, 0.0);
    driver->GetSpeedController().SetGains(0.4, 0.0, 0.0);
    driver->Initialize();

    // -----------------------------------------------
    // Visualization
    // -----------------------------------------------
    auto vis = chrono_types::make_shared<ChWheeledVehicleVisualSystemIrrlicht>();
    vis->SetWindowTitle("Lap Sim - Endurance 2025");
    vis->SetWindowSize(1280, 720);
    vis->SetChaseCamera(ChVector3d(0, 0, 1.0), 6.0, 0.5);
    vis->Initialize();
    vis->AddSkyBox();
    vis->AddLogo();
    vis->AddLightDirectional();
    vis->AttachVehicle(vehicle.get());

    // Marker spheres: red = sentinel, green = target
    auto sentinel_shape = chrono_types::make_shared<ChVisualShapeSphere>(0.1);
    auto target_shape   = chrono_types::make_shared<ChVisualShapeSphere>(0.1);
    sentinel_shape->SetColor(ChColor(1, 0, 0));
    target_shape->SetColor(ChColor(0, 1, 0));
    int sentinel_id = vis->AddVisualModel(sentinel_shape, ChFrame<>());
    int target_id   = vis->AddVisualModel(target_shape,   ChFrame<>());

    // -----------------------------------------------
    // Simulation loop
    // -----------------------------------------------
    const double step_size = 3e-3;

    while (vis->Run()) {
        double time = system.GetChTime();

        DriverInputs inputs = driver->GetInputs();

        vis->UpdateVisualModel(sentinel_id,
            ChFrame<>(driver->GetSteeringController().GetSentinelLocation()));
        vis->UpdateVisualModel(target_id,
            ChFrame<>(driver->GetSteeringController().GetTargetLocation()));

        vis->BeginScene();
        vis->Render();
        vis->EndScene();

        driver->Synchronize(time);
        terrain.Synchronize(time);
        vehicle->Synchronize(time, inputs, terrain);
        vis->Synchronize(time, inputs);

        driver->Advance(step_size);
        terrain.Advance(step_size);
        vehicle->Advance(step_size);
        vis->Advance(step_size);

        system.DoStepDynamics(step_size);
    }

    return 0;
}
