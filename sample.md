# Smartphone Camera Technology
> A training guide for product & marketing teams

## Module 1: Camera Fundamentals

### What is a Camera Module?
- A complete optical system packed into millimeters
- Contains sensor, lens, autofocus, OIS, and IR filter
- Five stacked layers from lens to circuit board
- Each layer adds capability but also Z-height cost

### The Five-Layer Stack
- Lens assembly — focuses light onto the sensor
- IRCF (IR cut filter) — blocks infrared light for accurate color
- CMOS sensor — converts photons into electrical signals
- VCM actuator — drives autofocus movement
- Flex PCB — carries data and power to the main board

### Key Sensor Specs
- Pixel size: larger pixels capture more light
- Optical format: bigger sensor = better low-light but more space
- Resolution: megapixels matter less than pixel quality
- BSI vs stacked architecture trade-offs

### Autofocus Technologies

```
Technology   Speed    Cost   Thickness
─────────────────────────────────────
PDAF         Fast     Low    Thin
Laser ToF    Medium   High   Moderate
DW-PDAF      Fastest  High   Thin
```

## Module 2: Physical Constraints

### The Z-Height Problem
- Every millimeter of thickness is a design battle
- OIS mechanism alone adds ~0.3 mm
- Larger sensors require longer focal length
- Periscope design folds the optics sideways

### OIS vs Thinness Trade-off
- OIS requires mechanical float — uses space
- Without OIS, night shots blur from hand movement
- Sensor-shift OIS moves sensor, not lens
- Decision depends on target use case and price tier

### Periscope Architecture
- Prism bends light 90° inside the module
- Achieves 5–10× optical zoom in a thin body
- XY footprint trades off against Z savings
- Flagship phones only — high cost and complexity

## Module 3: Multi-Camera Systems

### Why Multiple Cameras?
- Single lens can't do wide + zoom + portrait simultaneously
- Each focal length needs its own optical system
- Software stitches views during capture and zoom transitions
- ISP coordinates exposure across all sensors in real time

### Camera Roles in a Typical Flagship
- Ultra-wide (13–16 mm): architecture, landscapes, selfies
- Main (24–28 mm): everyday shooting, best IQ
- Periscope tele (65–120 mm): portraits, reach, compression

# Thank You
> Questions? Reach out to the product team.
