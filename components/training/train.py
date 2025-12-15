import argparse
from ultralytics import YOLO
import os
import yaml
from pathlib import Path

def find_dataset_root(data_path):
    """
    Find the dataset root directory that contains data.yaml.
    The dataset might be in gun-dataset/ or in a subdirectory like 
    gun-dataset/Gun with webcam views.v1i.yolov8/
    """
    data_path = Path(data_path)
    print(f"Searching for dataset root in: {data_path}")
    print(f"Path exists: {data_path.exists()}")
    print(f"Is directory: {data_path.is_dir()}")
    
    # Check if data_path itself contains data.yaml
    yaml_path = data_path / "data.yaml"
    print(f"Checking for data.yaml at: {yaml_path}")
    if yaml_path.exists():
        print(f"Found data.yaml at root: {data_path}")
        return data_path
    
    # Check subdirectories for YOLOv8 format datasets
    if data_path.is_dir():
        try:
            subdirs = list(data_path.iterdir())
            print(f"Found {len(subdirs)} items in data path")
            for subdir in subdirs:
                if subdir.is_dir():
                    print(f"Checking subdirectory: {subdir}")
                    if (subdir / "data.yaml").exists():
                        print(f"Found data.yaml in subdirectory: {subdir}")
                        return subdir
        except Exception as e:
            print(f"Error iterating directories: {e}")
            raise
    
    # If no data.yaml found, return the original path
    print(f"Warning: No data.yaml found, using original path: {data_path}")
    return data_path

def create_data_yaml(dataset_root, output_path="local_data.yaml"):
    """
    Create a data.yaml file with absolute paths for YOLOv8 training.
    Handles both the expected structure and the actual YOLOv8 format.
    """
    dataset_root = Path(dataset_root)
    
    # Check if data.yaml already exists
    existing_yaml = dataset_root / "data.yaml"
    if existing_yaml.exists():
        # Read existing yaml to get class names
        with open(existing_yaml, 'r') as f:
            existing_config = yaml.safe_load(f)
        
        # Get class names and count from existing config
        nc = existing_config.get('nc', 1)
        names = existing_config.get('names', ['gun'])
        
        # Determine paths based on actual structure
        # Check for YOLOv8 format: train/images, train/labels, valid/images, valid/labels
        train_path = None
        val_path = None
        
        if (dataset_root / "train" / "images").exists():
            # YOLOv8 format: train/images, valid/images
            train_path = str(dataset_root / "train" / "images")
            if (dataset_root / "valid" / "images").exists():
                val_path = str(dataset_root / "valid" / "images")
            elif (dataset_root / "val" / "images").exists():
                val_path = str(dataset_root / "val" / "images")
        elif (dataset_root / "images" / "train").exists():
            # Expected format: images/train, images/val
            train_path = str(dataset_root / "images" / "train")
            if (dataset_root / "images" / "val").exists():
                val_path = str(dataset_root / "images" / "val")
            elif (dataset_root / "images" / "valid").exists():
                val_path = str(dataset_root / "images" / "valid")
        else:
            # Fallback: assume images are in train/ and val/ directly
            if (dataset_root / "train").exists():
                train_path = str(dataset_root / "train")
            if (dataset_root / "val").exists():
                val_path = str(dataset_root / "val")
            elif (dataset_root / "valid").exists():
                val_path = str(dataset_root / "valid")
        
        if not train_path:
            raise ValueError(f"Could not find training images in {dataset_root}")
        
        # Create data config with absolute paths
        data_config = {
            'path': str(dataset_root),
            'train': train_path,
            'val': val_path if val_path else train_path,  # Use train as val if val not found
            'nc': nc,
            'names': names if isinstance(names, list) else list(names.values())
        }
    else:
        # No existing yaml, create default config
        # Try to detect structure
        if (dataset_root / "train" / "images").exists():
            train_path = str(dataset_root / "train" / "images")
            val_path = str(dataset_root / "valid" / "images") if (dataset_root / "valid" / "images").exists() else str(dataset_root / "val" / "images")
        else:
            train_path = str(dataset_root / "images" / "train")
            val_path = str(dataset_root / "images" / "val")
        
        data_config = {
            'path': str(dataset_root),
            'train': train_path,
            'val': val_path if val_path and Path(val_path).exists() else train_path,
            'nc': 1,
            'names': ['gun']
        }
    
    # Write the config
    with open(output_path, "w") as f:
        yaml.dump(data_config, f, default_flow_style=False)
    
    print(f"Created data.yaml at {output_path}")
    print(f"Training images: {data_config['train']}")
    print(f"Validation images: {data_config['val']}")
    print(f"Classes: {data_config['names']}")
    
    return output_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, help="Path to input data")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--model_output", type=str, help="Path to save model")
    args = parser.parse_args()

    print(f"Starting training script...")
    print(f"Data path argument: {args.data_path}")
    print(f"Epochs: {args.epochs}")
    print(f"Model output: {args.model_output}")
    
    # Check if data_path exists
    data_path = Path(args.data_path)
    if not data_path.exists():
        raise ValueError(f"Data path does not exist: {args.data_path}")
    
    print(f"Data path exists: {data_path}")
    print(f"Data path contents: {list(data_path.iterdir())[:10] if data_path.is_dir() else 'Not a directory'}")
    
    # Find the dataset root (handles nested structures)
    try:
        dataset_root = find_dataset_root(args.data_path)
        print(f"Dataset root found: {dataset_root}")
    except Exception as e:
        print(f"Error finding dataset root: {e}")
        raise
    
    # Create data.yaml with proper paths
    try:
        data_yaml_path = create_data_yaml(dataset_root)
        print(f"Data YAML created at: {data_yaml_path}")
    except Exception as e:
        print(f"Error creating data YAML: {e}")
        raise

    # Load a model
    print("Loading YOLOv8 model...")
    try:
        model = YOLO("yolov8n.pt")  # load a pretrained model
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

    # Train the model
    print(f"Starting training for {args.epochs} epochs...")
    print(f"Using data config: {data_yaml_path}")
    try:
        # Optimize for speed: smaller image size, fewer workers, disable plots for faster training
        train_kwargs = {
            'data': data_yaml_path,
            'epochs': args.epochs,
            'imgsz': 416 if args.epochs == 1 else 640,  # Smaller for 1 epoch test
            'project': args.model_output,
            'name': "yolo_run",
            'workers': 4,  # Reduce workers for faster startup
            'batch': 16,  # Keep batch size reasonable
            'plots': args.epochs > 1,  # Disable plots for 1 epoch (saves time)
            'save': True,  # Ensure model is saved
            'save_period': 1,  # Save every epoch
        }
        
        # For 1 epoch test, use even more aggressive optimizations
        if args.epochs == 1:
            train_kwargs.update({
                'imgsz': 320,  # Even smaller for speed
                'workers': 2,  # Fewer workers
                'cache': False,  # No caching for single epoch
                'close_mosaic': 0,  # Disable mosaic augmentation
            })
        
        model.train(**train_kwargs)
        print("Training completed successfully")
    except Exception as e:
        print(f"Error during training: {e}")
        raise

    # Copy the best model to the output folder root for easy registration
    src_path = os.path.join(args.model_output, "yolo_run", "weights", "best.pt")
    dst_path = os.path.join(args.model_output, "best.pt")
    
    print(f"Looking for model at: {src_path}")
    if os.path.exists(src_path):
        # Create output directory if it doesn't exist
        os.makedirs(args.model_output, exist_ok=True)
        # Use copy instead of rename in case of cross-filesystem issues
        import shutil
        shutil.copy2(src_path, dst_path)
        print(f"Model saved to {dst_path}")
    else:
        # Try alternative paths
        alt_paths = [
            os.path.join(args.model_output, "weights", "best.pt"),
            os.path.join(args.model_output, "best.pt"),
        ]
        found = False
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                import shutil
                os.makedirs(args.model_output, exist_ok=True)
                shutil.copy2(alt_path, dst_path)
                print(f"Model found at {alt_path} and copied to {dst_path}")
                found = True
                break
        
        if not found:
            print("Error: best.pt not found!")
            print(f"Expected path: {src_path}")
            print(f"Output directory contents: {os.listdir(args.model_output) if os.path.exists(args.model_output) else 'Directory does not exist'}")
            # Don't fail here, let Azure ML handle it

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("=" * 50)
        print("FATAL ERROR:")
        print(str(e))
        print("=" * 50)
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 50)
        raise

