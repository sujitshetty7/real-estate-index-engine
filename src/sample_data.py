from src.models import RawListing

sample_listings = [
    # Group 1: Duplicate Plots in Shahapur
    RawListing(
        id="101",
        source="broker_site_a",
        raw_title="5 Guntha Plot in Shahapur",
        raw_area_text="5 Guntha",
        raw_price_text="₹92 Lakh",
        locality="Shahapur",
        image_phash="a1b2c3d4e5f60000",
        source_url="http://broker-a.com/101"
    ),
    RawListing(
        id="102",
        source="local_directory",
        raw_title="5445 sqft prime land Shahapur",
        raw_area_text="5445 sqft",
        raw_price_text="9000000",
        locality="Shahapur",
        image_phash="a1b2c3d4e5f60000", # Exact same hash
        source_url="http://local-directory.com/102"
    ),
    RawListing(
        id="103",
        source="instagram",
        raw_title="Shahapur plot 5 guntha",
        raw_area_text="0.125 Acre",
        raw_price_text="91 Lakh",
        locality="Shahapur",
        image_phash="a1b2c3d4e5f60000", # Similar hash, distance < 6
        source_url="http://instagram.com/103"
    ),

    # Group 2: Distinct Plot in Shahapur
    RawListing(
        id="104",
        source="broker_site_b",
        raw_title="10 Guntha Plot Shahapur",
        raw_area_text="10 Guntha",
        raw_price_text="1.8 Cr",
        locality="Shahapur",
        image_phash="f8e7d6c5b4a39210",
        source_url="http://broker-b.com/104"
    ),

    # Group 3: Another Duplicate Set in Karjat
    RawListing(
        id="201",
        source="broker_site_a",
        raw_title="2 Acres Farm Land in Karjat",
        raw_area_text="2 Acre",
        raw_price_text="2.5 Crore",
        locality="Karjat",
        image_phash="1122334455667788",
        source_url="http://broker-a.com/201"
    ),
    RawListing(
        id="202",
        source="local_directory",
        raw_title="Karjat farmland 2 acres",
        raw_area_text="87120 sq ft",
        raw_price_text="2.55 Cr",
        locality="Karjat",
        image_phash="1122334455667788",
        source_url="http://local-directory.com/202"
    ),
    RawListing(
        id="203",
        source="broker_site_b",
        raw_title="Farm land 2 acre Karjat",
        raw_area_text="2 Acre",
        raw_price_text="2.6 Cr",
        locality="Karjat",
        image_phash="1122334455667799", # Very similar
        source_url="http://broker-b.com/203"
    ),

    # Group 4: Different location, similar stats
    RawListing(
        id="301",
        source="broker_site_a",
        raw_title="2 Acres Farm Land in Lonavala",
        raw_area_text="2 Acre",
        raw_price_text="3.0 Crore",
        locality="Lonavala",
        image_phash="1122334455667788", # Same visual, different locality - should not match Karjat
        source_url="http://broker-a.com/301"
    ),

    # Group 5: Small plots in Lonavala
    RawListing(
        id="302",
        source="instagram",
        raw_title="1 Guntha NA Plot Lonavala",
        raw_area_text="1 Guntha",
        raw_price_text="15 Lakh",
        locality="Lonavala",
        image_phash="abcdef1234567890",
        source_url="http://instagram.com/302"
    ),
    RawListing(
        id="303",
        source="local_directory",
        raw_title="Lonavala 1 guntha plot NA",
        raw_area_text="1089 sq ft",
        raw_price_text="14.5 Lacs",
        locality="Lonavala",
        image_phash="abcdef1234567890",
        source_url="http://local-directory.com/303"
    )
]
