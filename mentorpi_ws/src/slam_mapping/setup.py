from setuptools import setup

package_name = "slam_mapping"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", ["config/slam_toolbox.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="SLAM configuration placeholders for the MentorPi mapping stack.",
    license="MIT",
)
