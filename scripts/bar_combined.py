import pandas as pd
import matplotlib.pyplot as plt
import shared_config as sc
import os
import sys
import re
from PIL import Image
import matplotlib.patches as mpatches
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader


def add_to_pdf(pdf_path, image_paths, shift_constant, addition):
    output_file = PdfWriter()
    input_file = PdfReader(open(pdf_path, "rb"))
    input_page = input_file.pages[0]

    graphs = []
    for i, image in enumerate(image_paths):
        pdf_file = image.split(".")[0] + ".pdf"
        c = canvas.Canvas(
            pdf_file, pagesize=(input_page.mediabox.width, input_page.mediabox.width)
        )

        c.scale(0.72, 0.72)
        c.drawImage(image, i * shift_constant, 0, mask="auto")
        c.save()

        graph = PdfReader(open(pdf_file, "rb"))
        graphs.append(graph)
        input_page.merge_page(graph.pages[0])

    output_file.add_page(input_page)

    with open(
        f"{sc.plots_directory}players-bar-combined-{addition}.pdf", "wb"
    ) as outputStream:
        output_file.write(outputStream)
    print(f"Combined PDF saved to {sc.plots_directory}players-bar-combined-{addition}.pdf")
    for graph in graphs:
        graph.stream.close()
    
    input_file.stream.close()


def overlay_images(base_image_path, overlay_images_paths, shift_constant):
    base_image = Image.open(base_image_path).convert("RGBA")
    print(base_image_path)

    for i, overlay_image_path in enumerate(overlay_images_paths):
        print(overlay_image_path)
        overlay_image = Image.open(overlay_image_path).convert("RGBA")

        horizontal_shift = i * shift_constant

        new_image_width = base_image.width + horizontal_shift
        new_image_height = max(base_image.height, overlay_image.height)
        new_image = Image.new("RGBA", (new_image_width, new_image_height), (0, 0, 0, 0))

        new_image.paste(base_image, (0, 0), base_image)

        new_image.paste(overlay_image, (horizontal_shift, 0), overlay_image)

        base_image = new_image

    return base_image


def sort_list2_by_list1(list1, list2):
    order_dict = {value: index for index, value in enumerate(list1)}

    def extract_key(item):
        key_part = item.split(".")[0]
        return order_dict.get(key_part, float("inf"))

    sorted_list2 = sorted(list2, key=extract_key)

    return sorted_list2


def create_bar_graph(all_data=False, logic=False):
    player_experiments = [
        f"{sc.data_directory}{x}/"
        for x in os.listdir(sc.data_directory)
        if "players" in x
    ]
    average_csvs = [exp + "averaged_output.csv" for exp in player_experiments]

    order = [
        "Dummy",
        "Empty",
        "Empty (Logic Active)",
        "2-Layer (Logic Active)",
        "RollingHills",
        "RollingHills (Logic Active)",
    ]
    patterns = ["", "/", "-", "x", "o", ".", "*"]
    
    columns = [
            "StatisticsSystem",
            "PlayerTerrainGenCheck",
            "TerrainGeneration",
            "StructureGeneration",
            "TerrainLogicSystem",
        ]
    ybound = 0.75
    if all_data:
        columns = [
            "Main Thread_other",
            "ServerFixedUpdate_other",
        ] + columns
        ybound = 8.5
    elif logic:
        columns = [
            "TerrainLogicSystem_other",
            "GetUpdates",
            "ReevaluatePropagateMarker",
            "PropInputBlocks",
            "PropActiveLogicBlocks",
            "CheckGateState",
        ]
        ybound = 0.08
    addition = 2 if all_data else 3 if logic else 1

    output_files = []
    for average_csvs in average_csvs:
        if not os.path.exists(average_csvs):
            print(f"{average_csvs} does not exist")
            continue

        average_df = pd.read_csv(average_csvs)
        average_df.set_index("players", inplace=True)

        search = re.search(r"players(.+)\/", average_csvs)
        if search:
            val = search.group(1)
            if "-activeLogic" in val:
                val = f"{val.replace('-activeLogic_', '')} (Logic Active)"
            else:
                val = val.replace("_", "")
        else:
            raise ValueError("Invalid experiment name")

       

        x = average_df.index
        y = average_df[columns] / 1e6

        total_width = 0.9
        bar_width = total_width / len(order)
        hatching_index = order.index(val)

        ax = y.plot(
            kind="bar", stacked=True, figsize=(10, 6), width=bar_width, legend=False
        )

        ax.set_xlabel("Players")
        ax.set_ylabel("Time (ms)")
        
        ax.set_ybound(0, ybound)
        
        extension = "png"
        transparent = True
        if val == "Dummy":
            first_legend = ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
            ax.add_artist(first_legend)
            ax.figure.set_figwidth(13.5)
            transparent = False
            ax.set_xlim(-0.5, len(x) - 0.5)

            box = ax.get_position()
            ax.set_position([box.x0 * 0.8, box.y0, box.width * 0.77, box.height])

            legend_marker = []
            for order_val in order[1:]:
                circ = mpatches.Patch(
                    facecolor="white",
                    edgecolor="black",
                    hatch=patterns[order.index(order_val)],
                    label=order_val,
                )
                legend_marker.append(circ)
            ax.legend(handles=legend_marker, loc="center", bbox_to_anchor=(1.22, 0.2))
            extension = "pdf"
        else:
            ax.set_axis_off()
            bars = ax.patches
            pattern = patterns[
                hatching_index
            ]  
            hatches = []  
            for i in range(int(len(bars))):
                hatches.append(pattern)
            for bar, hatch in zip(
                bars, hatches
            ):  
                bar.set_hatch(hatch)

        ax.set_xticklabels(x, rotation=0)
        ax.tick_params(bottom=False)

        output_filename = f"{val}.{extension}"
        output_files.append(output_filename)
        ax.figure.savefig(output_filename, transparent=transparent, format=extension)
        # plt.close(fig)

    output_files = sort_list2_by_list1(order, output_files)

    add_to_pdf(output_files[0], output_files[1:], 13, addition)

    for helper_file in os.listdir():
        if helper_file.endswith(".pdf") or helper_file.endswith(".png"):
            os.remove(helper_file)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "all":
            create_bar_graph(True)
        elif sys.argv[1] == "logic":
            create_bar_graph(False, True)
        else:
            print("Invalid argument. Usage: python3 bar_combined.py [all]")
    else:
        create_bar_graph()
