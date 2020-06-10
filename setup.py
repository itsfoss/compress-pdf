from setuptools import setup, find_packages

setup(
    name="compress-pdf",
    version="0.1",
    author="ItsFOSS",
    author_email="",
    url="https://www.itsfoss.com",
    description="A PDF compressor GUI application",
    packages=["CompressPDF", "Config"],
    data_files=[("itsfoss/resources/compress-pdf", ["resources/inboxx.png", "resources/its.png", "resources/pdff.png"])],
    entry_points={
        "console_scripts": [
            "compress-pdf = CompressPDF.app:main"
        ]
    }
)
