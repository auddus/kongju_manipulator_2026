import os
import stat
from glob import glob

from setuptools import find_packages, setup

package_name = "tf2_basic"

console_scripts = {
    "static_turtle_tf2_broadcaster": "tf2_basic.static_turtle_tf2_broadcaster",
    "dynamic_turtle_tf2_broadcaster": "tf2_basic.dynamic_turtle_tf2_broadcaster",
    "tf_listener": "tf2_basic.tf_listener",
    "turtle_tf_listener": "tf2_basic.turtle_tf_listener",
    "move_u2d2": "tf2_basic.move_u2d2",
    "move_manipulator": "tf2_basic.move_manipulator",
    "dance_manipulator": "tf2_basic.dance_manipulator",
}

script_dir = os.path.join(os.path.dirname(__file__), "scripts")
os.makedirs(script_dir, exist_ok=True)
for script_name, module_name in console_scripts.items():
    script_path = os.path.join(script_dir, script_name)
    with open(script_path, "w", encoding="utf-8") as handle:
        handle.write("#!/usr/bin/env python3\n")
        handle.write(f"from {module_name} import main\n")
        handle.write("if __name__ == '__main__':\n")
        handle.write("    main()\n")
    os.chmod(
        script_path,
        stat.S_IRUSR
        | stat.S_IWUSR
        | stat.S_IXUSR
        | stat.S_IRGRP
        | stat.S_IXGRP
        | stat.S_IROTH
        | stat.S_IXOTH,
    )

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob(os.path.join("launch", "*.launch.py"))),
        ("share/" + package_name + "/urdf", glob(os.path.join("urdf", "*.*"))),
        ("share/" + package_name + "/rviz", glob(os.path.join("rviz", "*.*"))),
        ("share/" + package_name + "/meshes", glob(os.path.join("meshes", "*.*"))),
        ("share/" + package_name + "/config", glob(os.path.join("config", "*.yaml"))),
        ("lib/" + package_name, [os.path.join(script_dir, name) for name in console_scripts]),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="myung",
    maintainer_email="coolhk03@gmail.com",
    description="tf2 basic code for tutorial",
    license="Apache 2.0",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": [
            f"{name} = {module}:main" for name, module in console_scripts.items()
        ],
    },
)