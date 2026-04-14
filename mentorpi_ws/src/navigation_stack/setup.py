from setuptools import setup

package_name = "navigation_stack"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/config", ["config/nav2_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="Navigation configuration placeholders for Nav2 integration.",
    license="MIT",
)
