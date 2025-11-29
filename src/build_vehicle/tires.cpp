#include "tires.h"

using namespace chrono::vehicle;

ChPac02Tire build_tire() {
    ChPac02Tire tire("tire");

    tire.SetMFParamsByFile("lap_sim/data/tir/43070 Hoosier LC0 16x7.5-10 RIM 7 10 PSI.tir");
    return tire;
}