from __future__ import annotations

from outofthisworld.api_models import BodySnapshot, CraftSnapshot, Frame, SensorReading, frame_to_dict


def test_frame_to_dict_shape():
    frame = Frame(
        t_s=1.0,
        bodies=[
            BodySnapshot(
                id="earth",
                name="Earth",
                kind="planet",
                position_m=(1.0, 2.0, 3.0),
                radius_m=6_371_000.0,
                color="#3366ff",
            )
        ],
        craft=[
            CraftSnapshot(
                id="craft-1",
                name="Probe",
                position_m=(0.0, 0.0, 0.0),
                velocity_mps=(1.0, 0.0, 0.0),
                attitude_quat=(0.0, 0.0, 0.0, 1.0),
                sensors=[SensorReading(id="imu", kind="imu", value={"ax": 0.1})],
            )
        ],
        events=[{"kind": "note", "value": "hello"}],
    )

    data = frame_to_dict(frame)
    assert isinstance(data, dict)
    assert data["t_s"] == 1.0
    assert isinstance(data["bodies"], list)
    assert isinstance(data["craft"], list)
    assert isinstance(data["events"], list)

    body = data["bodies"][0]
    assert body["kind"] == "planet"
    assert body["position_m"] == [1.0, 2.0, 3.0]

    craft = data["craft"][0]
    assert craft["attitude_quat"] == [0.0, 0.0, 0.0, 1.0]
    assert craft["sensors"][0]["value"]["ax"] == 0.1

