# Robot Hardware Specs & Architecture

## Drivetrain

| Parameter | Value |
|---|---|
| Wheelbase | 167mm (0.167m) |
| Wheel diameter | 69mm (0.069m) |
| Wheel radius | 34.5mm (0.0345m) |
| Wheel circumference | π × 0.069 = 0.2168m |
| Encoder ticks per wheel revolution | 1920 |
| Distance per tick | circumference / ticks_per_rev = 0.2168 / 1920 = 0.0001129m |
| Gear ratio | 120:1 (16 pulses/motor rev × 120 = 1920 ticks/wheel rev) |

## Serial Protocol (Pi ↔ Arduino)

| Direction | Format |
|---|---|
| Pi → Arduino | `VEL {left_mps:.2f} {right_mps:.2f}\n` |
| Arduino → Pi | `ENC {left_ticks} {right_ticks}` |

- Port: `/dev/ttyACM0` at 115200 baud

## System Architecture

```
Sensors → Arduino Mega → Serial → Raspberry Pi 5 → 
                        ROS2 Jazzy
                           │
      ┌────────────────────┼────────────────────┐
      ▼                    ▼                    ▼
/odom topic          /imu/raw topic        /scan topic
      └────────────────────┼────────────────────┘
                           ▼
                        SLAM node
                           │
                     /map + /pose
                           │
                         nav2
                           │
                        /cmd_vel
                           │
                        Arduino → motors
```

## ROS2 Custom Nodes

| Node | Subscribes | Publishes | Purpose |
|---|---|---|---|
| `arduino_bridge` | `/cmd_vel` | `/odom`, `/imu/raw` | Serial bridge to Arduino |
| `lidar_node` | — | `/scan` | LiDAR data publisher |

## Components

- **Raspberry Pi 5** — high-level controller, ROS2, SLAM, navigation
- **Arduino Mega** — real-time motor control, encoder reading
- **LiDAR** — environment scanning
- **IMU (MPU6050)** — acceleration + angular velocity
- **Wheel encoders** — 1920 ticks/rev
- **2× DC motors** with gearboxes
- **3S LiPo** (~11.1V), buck converters to 5V for Pi and Arduino
