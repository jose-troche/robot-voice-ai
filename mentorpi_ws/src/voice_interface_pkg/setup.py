from setuptools import setup

package_name = "voice_interface_pkg"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools", "numpy", "sounddevice", "openai-whisper"],
    zip_safe=True,
    maintainer="Robot Voice AI",
    maintainer_email="user@example.com",
    description="Speech, intent routing, and spoken feedback nodes.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "speech_to_text_node = voice_interface_pkg.speech_to_text_node:main",
            "voice_command_router_node = voice_interface_pkg.voice_command_router_node:main",
            "text_to_speech_node = voice_interface_pkg.text_to_speech_node:main",
        ],
    },
)
