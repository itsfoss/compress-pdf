from setuptools import setup, find_packages

setup(
    name="Compress PDF",
    packages=find_packages(exclude=["tests*"]),
    package_data={},
    entry_points={
        'console_scripts': [
            'compress-pdf = compress_pdf:main'
        ],
    },

    data_files=[
        ('lib/python3/dist-packages/compress_pdf', ['its.png', 'inboxx.png', 'pdff.png']),
    ],
)
