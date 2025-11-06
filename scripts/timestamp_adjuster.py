import re
import sys
import argparse

def adjust_timestamps(text, hours_adjustment=-1):
    """
    Adjust all Discord timestamps in the text by the specified number of hours.
    By default, move them one hour earlier.

    Args:
        text (str): The input text containing Discord timestamps
        hours_adjustment (int): Number of hours to adjust (negative means earlier)

    Returns:
        str: The text with adjusted timestamps
    """
    seconds_adjustment = hours_adjustment * 3600

    def adjust_match(match):
        timestamp = int(match.group(1))
        new_timestamp = timestamp + seconds_adjustment
        return f"<t:{new_timestamp}:F>"

    pattern = r'<t:(\d+):F>'
    adjusted_text = re.sub(pattern, adjust_match, text)

    return adjusted_text

def main():
    parser = argparse.ArgumentParser(description="Adjust Discord timestamps in text files")
    parser.add_argument("input_file", help="Input file containing Discord timestamps")
    parser.add_argument("-o", "--output", help="Output file (default: adjusted_[input_file])")
    parser.add_argument("-t", "--time-shift", type=int,
                        help="Hours to adjust (negative = earlier, positive = later)")
    parser.add_argument("-d", "--direction", choices=["forward", "backward"],
                        help="Shortcut to shift by 1 hour forward or backward (default: backward)")
    args = parser.parse_args()

    if args.time_shift is not None and args.direction is not None:
        parser.error("Please specify either --time-shift or --direction, not both.")

    if args.time_shift is not None:
        hours_shift = args.time_shift
    elif args.direction is not None:
        hours_shift = 1 if args.direction == "forward" else -1
    else:
        hours_shift = -1

    output_file = args.output or f"adjusted_{args.input_file}"

    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()

        output_text = adjust_timestamps(input_text, hours_shift)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)

        direction_summary = 'later' if hours_shift > 0 else 'earlier' if hours_shift < 0 else 'unchanged'
        print(f"✓ Successfully adjusted timestamps by {hours_shift} hour(s) ({direction_summary}).")
        print(f"✓ Output saved to: {output_file}")
        print("\n--- Adjusted Text ---")
        print(output_text)

    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
