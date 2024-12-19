from flask import Flask, render_template, request, redirect, url_for, flash  # type: ignore


def generate_tattoo_design(keywords, max_images):
    # Dummy function to simulate AI design generation
    # In reality, you would connect to an AI model that generates the images based on keywords
    return [url_for('static', filename=f'sample_image_{i}.png') for i in range(1, max_images + 1)]
