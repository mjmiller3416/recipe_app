# helpers/rounded_image_label.py

#🔸Standard Library
from typing import Tuple, Union

# 🔸Third-party 
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel

# ────────────────────────────────────────────────────────────────────────────────


class StyledRoundedImageLabel(QLabel):
    """
    QLabel subclass that applies a rounded-corner mask via Qt style-sheets,
    leveraging Qt's vector-based rendering for perfectly smooth edges.

    Args:
        image_path (str): Path to the source image file.
        size (QSize): Target size for the label (width, height).
        radii (Union[int, Tuple[int, int, int, int]]): Corner radius in pixels.
            If an int, all four corners use the same radius.
            If a tuple, order is (top-left, top-right, bottom-right, bottom-left).
    """

    def __init__(
        self,
        image_path: str,
        size: QSize,
        radii: Union[int, Tuple[int, int, int, int]] = 20
    ) -> None:
        super().__init__()

        # normalize radii to four values
        if isinstance(radii, int):
            tl = tr = br = bl = radii
        elif isinstance(radii, (tuple, list)) and len(radii) == 4:
            tl, tr, br, bl = radii
        else:
            raise ValueError("radii must be an int or a 4-tuple of ints")

        self.setFixedSize(size)

        # construct the style-sheet with per-corner radii
        stylesheet = f"""
        QLabel {{
            border-image: url({image_path}) 0 0 0 0 stretch stretch;
            border-top-left-radius: {tl}px;
            border-top-right-radius: {tr}px;
            border-bottom-right-radius: {br}px;
            border-bottom-left-radius: {bl}px;
        }}
        """
        self.setStyleSheet(stylesheet)

# ── public methods ───────────────────────────────────────────────────
def create_rounded_image(
    image_path: str,
    dimension: int = 300,
    radii: Union[int, Tuple[int, int, int, int]] = 20
) -> StyledRoundedImageLabel:
    """
    Factory helper for StyledRoundedImageLabel.

    Args:
        image_path (str): Path to the source image.
        dimension (int): Width & height (square) in px.
        radii (int|tuple): Uniform or per-corner radii.
    """
    size = QSize(dimension, dimension)
    return StyledRoundedImageLabel(image_path, size, radii)


if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication(sys.argv)
    window = QWidget()
    # Set a dark background to preview edge smoothing
    window.setStyleSheet("background-color: #2c313c;")

    layout = QVBoxLayout(window)

    # Example: only top corners rounded
    label = create_rounded_image(
        image_path="recipe_images/beef_stroganoff.png",
        dimension=300,
        radii=(20, 20, 20, 20)  # All corners rounded
    )
    layout.addWidget(label)

    window.setWindowTitle("Styled Rounded Image Label Example")
    window.show()
    sys.exit(app.exec())
