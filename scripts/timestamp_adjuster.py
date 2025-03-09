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
    # Convert hours to seconds
    seconds_adjustment = hours_adjustment * 3600
    
    # Function to adjust the timestamp in each match
    def adjust_match(match):
        timestamp = int(match.group(1))
        new_timestamp = timestamp + seconds_adjustment
        return f"<t:{new_timestamp}:F>"
    
    # Find and replace all Discord timestamps
    pattern = r'<t:(\d+):F>'
    adjusted_text = re.sub(pattern, adjust_match, text)
    
    return adjusted_text

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Adjust Discord timestamps in text files")
    parser.add_argument("input_file", help="Input file containing Discord timestamps")
    parser.add_argument("-o", "--output", help="Output file (default: adjusted_[input_file])")
    parser.add_argument("-t", "--time-shift", type=int, default=-1,
                        help="Hours to adjust (negative = earlier, positive = later, default: -1)")
    args = parser.parse_args()
    
    # Determine output filename
    output_file = args.output or f"adjusted_{args.input_file}"
    
    try:
        # Read input file
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()
        
        # Adjust timestamps
        output_text = adjust_timestamps(input_text, args.time_shift)
        
        # Save to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        
        print(f"✓ Successfully adjusted timestamps by {args.time_shift} hour(s)")
        print(f"✓ Output saved to: {output_file}")
        
        # Also print the result for immediate viewing
        print("\n--- Adjusted Text ---")
        print(output_text)
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{args.input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

# Example usage
if __name__ == "__main__":
    main()