from setuptools import setup

package_name = "semantic_map_pkg"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/storage", ["storage/map_db.json"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="Semantic room and object memory for polygon-based spatial reasoning.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "semantic_map_node = semantic_map_pkg.semantic_map_node:main",
        ],
    },
)
