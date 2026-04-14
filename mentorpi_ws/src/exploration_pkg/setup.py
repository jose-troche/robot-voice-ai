from setuptools import setup

package_name = "exploration_pkg"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="Exploration and room annotation tools for polygon-based mapping.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "exploration_manager_node = exploration_pkg.exploration_manager_node:main",
        ],
    },
)
