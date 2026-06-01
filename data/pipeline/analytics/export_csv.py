import csv


def export_dwell_csv(
    results,
    output_file
):

    with open(
        output_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "visitor_id",
                "zone",
                "frames",
                "dwell_time_seconds"
            ]
        )

        for row in results:

            writer.writerow(
                [
                    row["visitor_id"],
                    row["zone"],
                    row["frames"],
                    row["dwell_time_seconds"]
                ]
            )