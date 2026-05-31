# pipeline/events/run_events.py

from line_counter import LineCounter
from event_generator import EventGenerator


def main():

    line_counter = LineCounter(
        line_start=(850, 1080),
        line_end=(1550, 0)
    )

    event_generator = EventGenerator()

    test_track = [
        (900, 950),
        (1000, 800),
        (1100, 650),
        (1200, 500),
        (1300, 350),
    ]

    visitor_id = "VIS_1"

    for frame_no, point in enumerate(test_track):

        event = line_counter.check_crossing(
            visitor_id,
            point
        )

        if event:

            event_generator.add_event(
                visitor_id,
                event,
                frame_no
            )

    event_generator.save_all()


if __name__ == "__main__":
    main()