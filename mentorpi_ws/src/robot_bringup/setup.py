from setuptools import setup

package_name = "robot_bringup"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (
            "share/" + package_name + "/launch",
            ["launch/robot_system.launch.py", "launch/smoke_test.launch.py"],
        ),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="Launch and bringup package for the MentorPi robot stack.",
    license="MIT",
)
