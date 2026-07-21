import os
from glob import glob

from setuptools import find_packages, setup

package_name = "gong_basic"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="auddus",
    maintainer_email="coolhk03@gmail.com",
    description="gongju university ROS2 basic library",
    license="Apache 2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            "simple_pub = gong_basic.simple_pub:main",
            "class_pub = gong_basic.class_pub:main",
            "class_sub = gong_basic.class_sub:main",
            "header_pub = gong_basic.header_pub:main",
            'mpub = gong_basic.mpub:main',
            'tpub = gong_basic.tpub:main',
            'msub = gong_basic.msub:main',
            'm2sub = gong_basic.msub:main2',
            'mtsub = gong_basic.mtsub:main',
            'mv_turtle = gong_basic.mv_turtle:main',
            'my_turtle2 = gong_basic.my_turtle2:main',
        ],
    },
)