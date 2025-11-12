"""
Command-line interface for ASTRA tools
"""
import argparse
import sys
import os

from .converters.json_to_qmd import convert_json_to_qmd, check_bib_file
from .converters.json_to_md import convert_json_to_markdown
from .bib.regenerate_keys import regenerate_bib_keys


def cmd_json_to_qmd(args):
    """Convert JSON to Quarto markdown (.qmd)"""
    json_file = args.json_file

    if not os.path.exists(json_file):
        print(f"❌ Error: File {json_file} not found")
        return 1

    # Check for .bib file
    print(f"Checking for bibliography file...")
    bib_file = check_bib_file(json_file)

    if not bib_file and not args.no_bib:
        # Check if we're in an interactive terminal
        if sys.stdin.isatty():
            response = input("\nContinue without bibliography file? (y/n): ")
            if response.lower() != 'y':
                print("Conversion cancelled. Please download the .bib file first.")
                return 1
        else:
            # Non-interactive mode: continue with warning
            print("⚠️  Continuing without bibliography file (non-interactive mode)")
            print("   Citations will not render correctly")

    try:
        print(f"\n📄 Converting {os.path.basename(json_file)} to Quarto markdown...")

        # Get custom CSL file if provided
        csl_file = getattr(args, 'csl_file', None)

        markdown_content, qmd_file, csl_filename = convert_json_to_qmd(
            json_file, bib_file, csl_file
        )

        # Write markdown file
        with open(qmd_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✅ Successfully converted to {os.path.basename(qmd_file)}")

        if bib_file:
            print(f"✅ Bibliography linked: {os.path.basename(bib_file)}")
            if csl_filename:
                print(f"✅ Citation style: {csl_filename}")
            print(f"\nYou can now render with: quarto render {qmd_file}")
        else:
            print(f"\n⚠️  Warning: No bibliography file found")
            print(f"   Citations will not render correctly without a .bib file")

        return 0

    except Exception as e:
        print(f"❌ Error converting file: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_json_to_md(args):
    """Convert JSON to markdown (.md)"""
    json_file = args.json_file

    if not os.path.exists(json_file):
        print(f"❌ Error: File {json_file} not found")
        return 1

    try:
        print(f"📄 Converting {os.path.basename(json_file)} to markdown...")
        markdown_content, markdown_file = convert_json_to_markdown(json_file)

        # Write markdown file
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"✅ Successfully converted to {os.path.basename(markdown_file)}")
        return 0

    except Exception as e:
        print(f"❌ Error converting file: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_regenerate_bib(args):
    """Regenerate citation keys in .bib file"""
    bib_file = args.bib_file

    if not os.path.exists(bib_file):
        print(f"❌ Error: File {bib_file} not found")
        return 1

    try:
        # Read original file
        with open(bib_file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        print(f"📖 Reading {os.path.basename(bib_file)}...")

        # Regenerate keys
        new_content, key_mapping = regenerate_bib_keys(original_content)

        print(f"✅ Regenerated {len(key_mapping)} citation keys")

        # Show mapping if requested or if verbose
        if args.show_mapping or args.verbose:
            print("\n📝 Key mappings:")
            for old_key, new_key in sorted(key_mapping.items()):
                if old_key != new_key:
                    print(f"   {old_key:30} -> {new_key}")

        # Write output
        if args.inplace:
            # Backup original
            backup_file = bib_file + '.backup'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"\n💾 Backed up original to {os.path.basename(backup_file)}")

            # Write new content
            with open(bib_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Updated {os.path.basename(bib_file)} in place")

        else:
            # Create new file
            output_file = os.path.splitext(bib_file)[0] + '.new.bib'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"\n✅ Created new file: {os.path.basename(output_file)}")
            print(f"   Review and rename to replace original if satisfied")

        # Save key mapping to a file for reference
        if args.save_mapping:
            mapping_file = os.path.splitext(bib_file)[0] + '_key_mapping.txt'
            with open(mapping_file, 'w', encoding='utf-8') as f:
                f.write("Old Key -> New Key\n")
                f.write("=" * 70 + "\n")
                for old_key, new_key in sorted(key_mapping.items()):
                    f.write(f"{old_key:30} -> {new_key}\n")

            print(f"📋 Key mapping saved to: {os.path.basename(mapping_file)}")

        return 0

    except Exception as e:
        print(f"❌ Error processing file: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='astra-convert',
        description='Convert ASTRA research reports to Quarto and Markdown formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert JSON to Quarto markdown
  astra-convert json-to-qmd report.json

  # Convert JSON to plain markdown
  astra-convert json-to-md report.json

  # Regenerate citation keys in bibliography
  astra-convert regenerate-bib report.bib

  # Regenerate citation keys in-place with backup
  astra-convert regenerate-bib report.bib --inplace

For more information, visit: https://astra.allen.ai
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed output and error traces'
    )

    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='Available conversion commands'
    )

    # json-to-qmd command
    parser_qmd = subparsers.add_parser(
        'json-to-qmd',
        help='Convert ASTRA JSON to Quarto markdown (.qmd)',
        description='Convert ASTRA JSON artifact to Quarto markdown with bibliography support'
    )
    parser_qmd.add_argument(
        'json_file',
        help='Path to ASTRA JSON file'
    )
    parser_qmd.add_argument(
        '--no-bib',
        action='store_true',
        help='Skip bibliography file check and proceed without prompting'
    )
    parser_qmd.add_argument(
        '--csl-file',
        dest='csl_file',
        metavar='CSL_FILE',
        help='Path to custom CSL file (default: uses bundled apa.csl)'
    )
    parser_qmd.set_defaults(func=cmd_json_to_qmd)

    # json-to-md command
    parser_md = subparsers.add_parser(
        'json-to-md',
        help='Convert ASTRA JSON to plain markdown (.md)',
        description='Convert ASTRA JSON artifact to plain markdown'
    )
    parser_md.add_argument(
        'json_file',
        help='Path to ASTRA JSON file'
    )
    parser_md.set_defaults(func=cmd_json_to_md)

    # regenerate-bib command
    parser_bib = subparsers.add_parser(
        'regenerate-bib',
        help='Regenerate citation keys in .bib file',
        description='Regenerate citation keys using convention: AuthorYearTitleWords'
    )
    parser_bib.add_argument(
        'bib_file',
        help='Path to .bib file'
    )
    parser_bib.add_argument(
        '--inplace',
        action='store_true',
        help='Modify file in place (creates .backup)'
    )
    parser_bib.add_argument(
        '--show-mapping',
        action='store_true',
        help='Display key mappings after regeneration'
    )
    parser_bib.add_argument(
        '--save-mapping',
        action='store_true',
        help='Save key mappings to a text file'
    )
    parser_bib.set_defaults(func=cmd_regenerate_bib)

    # Parse arguments
    args = parser.parse_args()

    # Show help if no command specified
    if not args.command:
        parser.print_help()
        return 1

    # Execute the command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
