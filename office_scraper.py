#!/usr/bin/env python3
"""
Musical Instruments Image Downloader using icrawler
Downloads images of musical instruments and saves them with descriptive filenames.
"""

import os
import time
import sys
import random
from icrawler.builtin import GoogleImageCrawler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# List of musical instruments (easy + hard mix)
musical_instruments = [
    "Piano", "Guitar", "Electric guitar", "Bass guitar", "Drum set", "Violin", "Viola", "Cello", "Double bass", "Trumpet",
    "Trombone", "French horn", "Tuba", "Clarinet", "Flute", "Oboe", "Bassoon", "Piccolo", "Saxophone", "Harmonica",
    "Accordion", "Mandolin", "Banjo", "Ukulele", "Marimba", "Xylophone", "Glockenspiel", "Steel drum", "Djembe", "Conga drum",
    "Bongo drums", "Tambourine", "Triangle", "Castanets", "Guiro", "Cajón", "Bagpipes", "Didgeridoo", "Sitar", "Tabla",
    "Kalimba", "Zither", "Lute", "Ocarina", "Pan flute", "Recorder", "Shakuhachi", "Erhu", "Koto", "Shamisen",
    "Sarangi", "Hardanger fiddle", "Bouzouki", "Balalaika", "Mandocello", "Clavichord", "Harpsichord", "Hurdy-gurdy", "Melodica", "Synthesizer",
    "Keytar", "Organ", "Pipe organ", "Glass harmonica", "Jaw harp", "Bass clarinet", "Contrabassoon", "English horn", "Oboe d'amore", "Cornet",
    "Sousaphone", "Slide whistle", "Waterphone", "Theremin", "Electronic drum pad", "Snare drum", "Bass drum", "Timpani", "Agogo bells", "Cowbell",
    "Handpan", "Hang drum", "Log drum", "Rainstick", "Vibraphone", "Celesta", "Bell lyre", "Toy piano", "Baritone horn", "Bugle",
    "Rebab", "Crwth", "Nyckelharpa", "Fujara", "Duduk", "Tumbi", "Santoor", "Berimbau", "Mbira", "Tsymbaly"
]

# Path to save images
save_directory = "/Users/collinschreyer/GSA/the_floor/musical_instruments"

def create_placeholder_image(item):
    try:
        filename = f"{item.replace(' ', '_')}.jpg"
        file_path = os.path.join(save_directory, filename)
        with open(file_path, 'wb') as f:
            f.write(bytes([
                0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
                0x01, 0x01, 0x00, 0x48, 0x00, 0x48, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
                *([0xFF] * 64), 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01, 0x00, 0x01,
                0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x14, 0x00, 0x01, 0x00, 0x00,
                *([0x00] * 12), 0xFF, 0xC4, 0x00, 0x14, 0x10, 0x01, 0x00, 0x00,
                *([0x00] * 12), 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00,
                0x3F, 0x00, 0x7F, 0x00, 0xFF, 0xD9
            ]))
        logger.info(f"✓ Created placeholder for {item}")
        return True
    except Exception as e:
        logger.error(f"× Error creating placeholder for {item}: {str(e)}")
        return False

def download_image_with_icrawler(item, max_num=1):
    try:
        safe_item_name = item.replace(' ', '_')
        item_dir = os.path.join(save_directory, safe_item_name)
        if not os.path.exists(item_dir):
            os.makedirs(item_dir)

        search_query = f"{item} musical instrument"
        logger.info(f"Searching for '{search_query}'...")

        google_crawler = GoogleImageCrawler(
            downloader_threads=4,
            storage={'root_dir': item_dir}
        )

        google_crawler.crawl(
            keyword=search_query,
            max_num=max_num,
            min_size=(200, 200),
            file_idx_offset=0
        )

        downloaded_files = os.listdir(item_dir)
        image_files = [f for f in downloaded_files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

        if len(image_files) > 0:
            first_image = image_files[0]
            first_image_path = os.path.join(item_dir, first_image)
            new_image_path = os.path.join(save_directory, f"{safe_item_name}.jpg")

            with open(first_image_path, 'rb') as src_file:
                with open(new_image_path, 'wb') as dest_file:
                    dest_file.write(src_file.read())

            logger.info(f"✓ Downloaded and saved image for {item}")
            return True
        else:
            logger.warning(f"× No images found for '{item}'")
            return False

    except Exception as e:
        logger.error(f"× Error downloading image for {item}: {str(e)}")
        return False

def main():
    logger.info(f"Starting download of {len(musical_instruments)} musical instruments...")
    logger.info(f"Images will be saved to: {save_directory}")

    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        logger.info(f"Created directory: {save_directory}")

    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
            logger.info(f"Limiting to first {limit} items (for testing)")
        except ValueError:
            pass

    items_to_process = musical_instruments[:limit] if limit else musical_instruments

    successful = 0
    failed = 0

    try:
        for item in items_to_process:
            logger.info(f"\nProcessing: {item}")

            if download_image_with_icrawler(item, max_num=3):
                successful += 1
            else:
                if create_placeholder_image(item):
                    successful += 1
                else:
                    failed += 1

            total_processed = successful + failed
            logger.info(f"Progress: {total_processed}/{len(items_to_process)} ({successful} successful, {failed} failed)")

            delay = random.uniform(2, 4)
            logger.info(f"Waiting {delay:.1f} seconds before next item...")
            time.sleep(delay)

    except KeyboardInterrupt:
        logger.warning("\nProcess interrupted by user.")
    except Exception as e:
        logger.error(f"\nUnexpected error: {str(e)}")

    logger.info("\nDownload complete!")
    logger.info(f"Successfully processed: {successful}/{len(items_to_process)} items")
    logger.info(f"Failed: {failed}/{len(items_to_process)} items")
    logger.info(f"Images are saved in: {save_directory}")

if __name__ == "__main__":
    main()
