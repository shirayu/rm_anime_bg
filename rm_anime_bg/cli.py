#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import onnxruntime as rt
from huggingface_hub.file_download import hf_hub_download

SCALE: int = 255


def get_mask(
    session_infer: rt.InferenceSession,
    img: np.ndarray,
    size_infer: int = 1024,
):
    img = (img / SCALE).astype(np.float32)
    h_orig, w_orig = img.shape[:-1]

    if h_orig > w_orig:
        h_infer, w_infer = (size_infer, int(size_infer * w_orig / h_orig))
    else:
        h_infer, w_infer = (int(size_infer * h_orig / w_orig), size_infer)

    h_padding, w_padding = size_infer - h_infer, size_infer - w_infer
    img_infer = np.zeros([size_infer, size_infer, 3], dtype=np.float32)
    img_infer[
        h_padding // 2 : h_padding // 2 + h_infer,
        w_padding // 2 : w_padding // 2 + w_infer,
    ] = cv2.resize(img, (w_infer, h_infer))
    img_infer = np.transpose(img_infer, (2, 0, 1))
    img_infer = img_infer[np.newaxis, :]

    mask = session_infer.run(None, {"img": img_infer})[0][0]
    mask = np.transpose(mask, (1, 2, 0))
    mask = mask[
        h_padding // 2 : h_padding // 2 + h_infer,
        w_padding // 2 : w_padding // 2 + w_infer,
    ]
    mask = cv2.resize(mask, (w_orig, h_orig))[:, :, np.newaxis]
    return mask


def save_image(
    *,
    img,
    output_dir: Path,
    path_original: Path,
    out_format,
):
    if path_original.parent == output_dir:
        raise FileExistsError(
            f"Output directory should not be the same directory of the input image: {output_dir}"
        )
    output_dir.mkdir(
        exist_ok=True,
        parents=True,
    )
    out_path: Path = output_dir.joinpath(path_original.stem + ".png")
    idx: int = 0
    while out_path.exists():
        out_path = output_dir.joinpath(f"{path_original.stem}.{idx}.png")
        idx += 1

    img = cv2.cvtColor(img, out_format)
    cv2.imwrite(str(out_path), img)


def operation(
    *,
    model_repo_id: str,
    model_filename: str,
    targets: List[str],
    output_matted: Optional[Path],
    output_dir: Optional[Path],
    alpha_min: float,
    alpha_max: float,
    force_cpu: bool,
) -> None:
    if output_matted is None and output_dir is None:
        raise ValueError("No output directory names are given")

    session_infer_path = hf_hub_download(
        repo_id=model_repo_id,
        filename=model_filename,
    )

    providers: list[str] = ["CPUExecutionProvider"]
    if not force_cpu and "CUDAExecutionProvider" in rt.get_available_providers():
        providers = ["CUDAExecutionProvider"]

    session_infer = rt.InferenceSession(
        session_infer_path,
        providers=providers,
    )

    for path in targets:
        img = cv2.cvtColor(cv2.imread(path, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        mask = get_mask(session_infer, img)

        mask[mask < alpha_min] = 0.0
        mask[mask > alpha_max] = 1.0

        img_after = (mask * img + SCALE * (1 - mask)).astype(np.uint8)
        mask = (mask * SCALE).astype(np.uint8)
        img_after = np.concatenate([img_after, mask], axis=2, dtype=np.uint8)
        mask = mask.repeat(3, axis=2)

        if output_dir:
            save_image(
                img=img_after,
                output_dir=output_dir,
                path_original=Path(path),
                out_format=cv2.COLOR_BGRA2RGBA,
            )

        if output_matted:
            save_image(
                img=mask,
                output_dir=output_matted,
                path_original=Path(path),
                out_format=cv2.COLOR_BGR2RGB,
            )


def get_opts():
    oparser = argparse.ArgumentParser()
    oparser.add_argument(
        "--model-repo-id",
        default="skytnt/anime-seg",
    )
    oparser.add_argument(
        "--model-filename",
        default="isnetis.onnx",
    )
    oparser.add_argument(
        "-o",
        "--output",
        type=Path,
    )
    oparser.add_argument(
        "--matted",
        type=Path,
    )
    oparser.add_argument(
        "--alpha-min",
        type=float,
        default=0.0,
    )
    oparser.add_argument(
        "--alpha-max",
        type=float,
        default=1.0,
    )
    oparser.add_argument(
        "--cpu",
        action="store_true",
        help="Force to use CPU",
    )
    return oparser.parse_known_args()


def main() -> None:
    (opts, targets) = get_opts()
    operation(
        model_repo_id=opts.model_repo_id,
        model_filename=opts.model_filename,
        targets=targets,
        output_dir=opts.output,
        output_matted=opts.matted,
        alpha_min=opts.alpha_min,
        alpha_max=opts.alpha_max,
        force_cpu=opts.cpu,
    )


if __name__ == "__main__":
    main()
