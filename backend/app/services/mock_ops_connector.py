"""Mock OPS connector with hardcoded patents for demo use when EPO credentials are absent."""

from __future__ import annotations

from app.services.ops_connector import RawPatentData

_PATENTS: dict[str, dict] = {
    "EP3456789A1": {
        "biblio": {
            "publication_number": "EP3456789A1",
            "title": "Neural network system for real-time data classification and anomaly detection",
            "applicants": ["DeepTech Systems GmbH"],
            "inventors": ["Müller, Hans", "Schneider, Anna"],
            "ipc_classes": ["G06N3/04", "G06F18/214"],
            "cpc_classes": ["G06N3/0454", "G06F18/2148"],
            "publication_date": "20190315",
            "priority_date": "20180901",
        },
        "abstract": (
            "A neural network system for classifying high-dimensional data streams in real time. "
            "The system comprises a multi-layer perceptron with adaptive learning rate scheduling, "
            "a sliding window preprocessing module, and an anomaly detection layer based on "
            "reconstruction error thresholding. The architecture supports online learning and "
            "can be retrained incrementally without full reinitialization. Applications include "
            "fraud detection, industrial fault monitoring, and network intrusion detection."
        ),
        "claims": (
            "1. A system for real-time classification comprising: a neural network having at least "
            "three hidden layers; an input pipeline for streaming time-series data; and an anomaly "
            "detection module that flags outputs deviating beyond a configurable threshold.\n"
            "2. The system of claim 1, wherein the neural network is retrained incrementally using "
            "a sliding window of recent observations."
        ),
        "legal_status": "Active",
    },
    "EP3234567B1": {
        "biblio": {
            "publication_number": "EP3234567B1",
            "title": "Machine learning model compression and optimization for edge computing devices",
            "applicants": ["EdgeAI Technologies Ltd"],
            "inventors": ["Chen, Wei", "Park, Jisoo"],
            "ipc_classes": ["G06N3/08", "G06F9/50"],
            "cpc_classes": ["G06N3/082", "G06F9/5061"],
            "publication_date": "20200722",
            "priority_date": "20190210",
        },
        "abstract": (
            "Methods and apparatus for compressing deep neural network models to enable deployment "
            "on resource-constrained edge devices. Techniques include structured pruning of "
            "redundant weight channels, post-training quantization to 8-bit integer precision, "
            "and knowledge distillation from a large teacher model to a compact student model. "
            "The resulting compressed model retains more than 95% of the original accuracy while "
            "reducing memory footprint by up to 75% and inference latency by 60%."
        ),
        "claims": (
            "1. A method of compressing a neural network model comprising: pruning weight channels "
            "with magnitude below a threshold; quantizing remaining weights to INT8; and distilling "
            "knowledge from a full-precision teacher network.\n"
            "2. The method of claim 1, wherein pruning is performed layer-wise with a per-layer "
            "sparsity target determined by sensitivity analysis."
        ),
        "legal_status": "Active",
    },
    "EP3678901A1": {
        "biblio": {
            "publication_number": "EP3678901A1",
            "title": "Autonomous vehicle perception system using multi-modal deep learning sensor fusion",
            "applicants": ["AutoDrive Innovations SA"],
            "inventors": ["Dupont, Claire", "Rossi, Marco"],
            "ipc_classes": ["B60W40/02", "G06V20/56"],
            "cpc_classes": ["B60W2040/0227", "G06V20/588"],
            "publication_date": "20200901",
            "priority_date": "20190301",
        },
        "abstract": (
            "A perception system for autonomous vehicles that fuses data from LiDAR, camera, and "
            "radar sensors using a transformer-based deep learning architecture. The system performs "
            "real-time 3D object detection and semantic segmentation to identify pedestrians, "
            "vehicles, and road infrastructure. A confidence-weighted late-fusion strategy combines "
            "modality-specific predictions, and a temporal attention module tracks object motion "
            "across frames. The system achieves state-of-the-art detection accuracy under adverse "
            "weather conditions including rain and fog."
        ),
        "claims": (
            "1. A perception system comprising: LiDAR, camera and radar sensors; a feature "
            "extraction network for each modality; a fusion module combining modality features "
            "via attention weights; and a detection head outputting 3D bounding boxes.\n"
            "2. The system of claim 1, wherein the fusion module uses cross-modal attention."
        ),
        "legal_status": "Active",
    },
    "EP2987654B1": {
        "biblio": {
            "publication_number": "EP2987654B1",
            "title": "Photovoltaic energy yield optimization using predictive machine learning algorithms",
            "applicants": ["SolarLogic GmbH"],
            "inventors": ["Fischer, Thomas", "Bauer, Maria"],
            "ipc_classes": ["H02S50/10", "G06N20/00"],
            "cpc_classes": ["H02S50/10", "G06N20/10"],
            "publication_date": "20171204",
            "priority_date": "20160715",
        },
        "abstract": (
            "A system and method for maximizing photovoltaic energy yield through predictive "
            "algorithms that integrate weather forecast data, historical irradiance measurements, "
            "and panel degradation models. A gradient boosting regressor predicts hourly energy "
            "output up to 72 hours in advance, enabling proactive grid dispatch scheduling. "
            "An online adaptation layer updates model parameters daily using incoming sensor "
            "readings to compensate for panel soiling and seasonal drift."
        ),
        "claims": (
            "1. A method for photovoltaic yield prediction comprising: ingesting weather forecast "
            "and historical irradiance data; training a gradient boosting model on said data; "
            "and generating hourly energy yield predictions for a rolling 72-hour horizon.\n"
            "2. The method of claim 1, further comprising updating model parameters daily."
        ),
        "legal_status": "Expired",
    },
    "EP3123456A1": {
        "biblio": {
            "publication_number": "EP3123456A1",
            "title": "Adaptive IoT sensor network with intelligent data aggregation and edge preprocessing",
            "applicants": ["SensorMesh Technologies BV"],
            "inventors": ["de Vries, Jan", "Kowalski, Piotr"],
            "ipc_classes": ["H04L67/12", "G16Y20/10"],
            "cpc_classes": ["H04L67/125", "G16Y20/10"],
            "publication_date": "20181120",
            "priority_date": "20170428",
        },
        "abstract": (
            "An IoT sensor network architecture with adaptive sampling rates and edge-side data "
            "aggregation to reduce cloud transmission bandwidth. Sensor nodes run lightweight "
            "anomaly detection models that trigger high-frequency sampling only when deviations "
            "are detected. A hierarchical aggregation protocol compresses readings using "
            "delta encoding before transmission. The system supports heterogeneous sensor types "
            "and dynamic topology reconfiguration without service interruption."
        ),
        "claims": (
            "1. An IoT network comprising: a plurality of sensor nodes; an edge aggregation layer; "
            "and a cloud backend; wherein each sensor node adapts its sampling rate based on a "
            "local anomaly score computed from recent readings.\n"
            "2. The network of claim 1, wherein aggregation uses delta encoding to compress data."
        ),
        "legal_status": "Active",
    },
    "EP3890123B1": {
        "biblio": {
            "publication_number": "EP3890123B1",
            "title": "Large-scale natural language processing system for automated document understanding",
            "applicants": ["LinguaAI Corp"],
            "inventors": ["Smith, James", "Nakamura, Yuki"],
            "ipc_classes": ["G06F40/30", "G06N3/04"],
            "cpc_classes": ["G06F40/30", "G06N3/0455"],
            "publication_date": "20220310",
            "priority_date": "20201114",
        },
        "abstract": (
            "A natural language processing system for automated understanding of long-form documents "
            "including contracts, scientific papers, and regulatory filings. The system uses a "
            "pre-trained transformer encoder fine-tuned with domain-specific corpora to extract "
            "named entities, key clauses, and semantic relationships. A hierarchical summarization "
            "module produces multi-level abstracts. The pipeline supports 40 languages and "
            "processes documents of arbitrary length through a sliding-window chunking strategy."
        ),
        "claims": (
            "1. A document understanding system comprising: a transformer encoder; an entity "
            "extraction head; a relation classification head; and a summarization module that "
            "produces summaries at sentence, paragraph, and document levels.\n"
            "2. The system of claim 1, wherein documents exceeding the context window are split "
            "into overlapping chunks that are independently encoded and then aggregated."
        ),
        "legal_status": "Active",
    },
    "EP2765432A1": {
        "biblio": {
            "publication_number": "EP2765432A1",
            "title": "Distributed ledger system for supply chain provenance tracking and transparency",
            "applicants": ["ChainVerify Ltd"],
            "inventors": ["Okafor, Chidi", "Larsson, Erik"],
            "ipc_classes": ["G06Q10/08", "H04L9/32"],
            "cpc_classes": ["G06Q10/0833", "H04L9/3236"],
            "publication_date": "20150820",
            "priority_date": "20140201",
        },
        "abstract": (
            "A blockchain-based system for recording and verifying provenance events across "
            "multi-tier supply chains. Each supply chain event is encoded as an immutable "
            "transaction on a permissioned distributed ledger. Smart contracts enforce compliance "
            "rules automatically upon event submission. QR-code and NFC-linked physical items "
            "are mapped to digital tokens, enabling end-to-end traceability from raw material "
            "origin to end consumer. The system integrates with existing ERP platforms via REST APIs."
        ),
        "claims": (
            "1. A supply chain tracking system comprising: a permissioned blockchain network; "
            "smart contracts encoding compliance rules; and a physical-to-digital linking module "
            "using QR codes or NFC tags.\n"
            "2. The system of claim 1, wherein each supply chain event is validated by a "
            "quorum of authorized validator nodes before being appended to the ledger."
        ),
        "legal_status": "Lapsed",
    },
    "EP3567890B1": {
        "biblio": {
            "publication_number": "EP3567890B1",
            "title": "Convolutional neural network architecture for automated medical image diagnosis",
            "applicants": ["MediVision AG"],
            "inventors": ["Hoffmann, Klaus", "Tanaka, Hiroshi"],
            "ipc_classes": ["G06T7/00", "A61B5/00"],
            "cpc_classes": ["G06T7/0012", "A61B5/7267"],
            "publication_date": "20210615",
            "priority_date": "20191022",
        },
        "abstract": (
            "A convolutional neural network system for diagnosing pathologies in radiology images "
            "including X-ray, CT, and MRI modalities. The architecture employs an encoder-decoder "
            "design with skip connections for pixel-level segmentation of lesions and tumors. "
            "Class activation mapping provides clinician-interpretable heatmaps highlighting "
            "regions influencing the diagnosis. The system achieves radiologist-level sensitivity "
            "on lung nodule detection benchmarks and integrates directly with PACS systems via "
            "DICOM protocol."
        ),
        "claims": (
            "1. A medical image diagnosis system comprising: a CNN encoder-decoder; a "
            "segmentation head producing pixel-level labels; and an interpretability module "
            "generating class activation maps.\n"
            "2. The system of claim 1, further comprising a DICOM interface for integration "
            "with hospital picture archiving and communication systems."
        ),
        "legal_status": "Active",
    },
    "EP3012345A1": {
        "biblio": {
            "publication_number": "EP3012345A1",
            "title": "Intelligent battery energy storage management with predictive load balancing",
            "applicants": ["GridSmart Energy Systems"],
            "inventors": ["Petrov, Dmitri", "Lindqvist, Sofia"],
            "ipc_classes": ["H02J7/00", "G05B13/04"],
            "cpc_classes": ["H02J7/0047", "G05B13/042"],
            "publication_date": "20160420",
            "priority_date": "20141105",
        },
        "abstract": (
            "A battery energy storage management system that uses model predictive control and "
            "machine learning to optimize charge/discharge cycles for grid-connected installations. "
            "The system forecasts demand load and renewable generation using an LSTM network "
            "trained on historical grid data. A linear programming optimizer schedules battery "
            "operation to minimize electricity cost while satisfying state-of-charge constraints "
            "and battery degradation limits. The system reduces peak demand charges by up to 40%."
        ),
        "claims": (
            "1. An energy storage management system comprising: an LSTM demand forecast module; "
            "a linear programming optimizer; and a battery controller that executes the optimized "
            "charge/discharge schedule.\n"
            "2. The system of claim 1, wherein the optimizer incorporates battery cycle-life "
            "degradation as a cost term."
        ),
        "legal_status": "Active",
    },
    "EP2876543B1": {
        "biblio": {
            "publication_number": "EP2876543B1",
            "title": "Federated learning framework for privacy-preserving distributed model training",
            "applicants": ["PrivacyML Research Institute"],
            "inventors": ["Gomez, Elena", "Wang, Lei"],
            "ipc_classes": ["G06N20/00", "H04L9/00"],
            "cpc_classes": ["G06N20/00", "H04L9/008"],
            "publication_date": "20190101",
            "priority_date": "20170630",
        },
        "abstract": (
            "A federated learning framework enabling multiple organizations to collaboratively "
            "train machine learning models without sharing raw data. Local models are trained "
            "on private datasets and only gradient updates are transmitted to a central aggregation "
            "server. Differential privacy noise is added to gradients before transmission to "
            "prevent membership inference attacks. Secure aggregation using homomorphic encryption "
            "ensures the server learns only the aggregated update. The framework supports "
            "heterogeneous data distributions and variable client participation."
        ),
        "claims": (
            "1. A federated learning system comprising: a central aggregation server; a plurality "
            "of client nodes each holding private data; a protocol for transmitting differentially "
            "private gradient updates; and a secure aggregation module using homomorphic encryption."
            "\n2. The system of claim 1, wherein clients are selected per round via a "
            "stratified sampling strategy."
        ),
        "legal_status": "Active",
    },
    "EP3345678A1": {
        "biblio": {
            "publication_number": "EP3345678A1",
            "title": "Computer vision quality control system for automated industrial defect detection",
            "applicants": ["InspectAI Solutions"],
            "inventors": ["Virtanen, Mikko", "Santos, Ana"],
            "ipc_classes": ["G06T7/00", "G01N21/88"],
            "cpc_classes": ["G06T7/0004", "G01N21/8851"],
            "publication_date": "20180710",
            "priority_date": "20160922",
        },
        "abstract": (
            "A computer vision system for inline quality inspection on manufacturing lines using "
            "high-resolution cameras and a real-time defect detection neural network. The system "
            "identifies surface defects including scratches, dents, discoloration, and dimensional "
            "deviations with sub-millimeter precision. A semi-supervised learning approach reduces "
            "the labeling burden by leveraging abundant unlabeled images from the production line. "
            "Defect statistics are fed back to process control systems to enable closed-loop "
            "manufacturing optimization."
        ),
        "claims": (
            "1. An industrial inspection system comprising: one or more high-resolution cameras; "
            "a defect detection neural network processing camera frames in real time; and a "
            "feedback interface to a process control system.\n"
            "2. The system of claim 1, wherein the neural network is trained using semi-supervised "
            "learning on labeled and unlabeled production images."
        ),
        "legal_status": "Active",
    },
    "EP3901234B1": {
        "biblio": {
            "publication_number": "EP3901234B1",
            "title": "Reinforcement learning system for adaptive robotic process automation",
            "applicants": ["RoboLearn Technologies"],
            "inventors": ["Ivanova, Natasha", "Kim, Daeho"],
            "ipc_classes": ["B25J9/16", "G06N3/08"],
            "cpc_classes": ["B25J9/163", "G06N3/088"],
            "publication_date": "20220908",
            "priority_date": "20210115",
        },
        "abstract": (
            "A reinforcement learning system enabling robots to autonomously adapt manipulation "
            "strategies for process automation tasks without explicit programming. The agent learns "
            "optimal pick-and-place, assembly, and inspection policies through simulated experience "
            "using a digital twin environment, then transfers learned policies to physical hardware "
            "via domain randomization. A reward shaping mechanism incorporates safety constraints "
            "and cycle time targets. The system reduces robot programming time by 80% compared "
            "to traditional teach-and-repeat methods."
        ),
        "claims": (
            "1. A robotic automation system comprising: a reinforcement learning agent; a digital "
            "twin simulation environment for policy training; a domain randomization module; and "
            "a sim-to-real transfer mechanism.\n"
            "2. The system of claim 1, wherein the reward function encodes safety constraints "
            "as hard penalties."
        ),
        "legal_status": "Active",
    },
}

_ALL_REFS = list(_PATENTS.keys())


class MockOpsConnector:
    """Drop-in replacement for OpsConnector using hardcoded patent data."""

    async def search_patents(self, cql: str, start: int = 0, rows: int = 100) -> list[RawPatentData]:
        return [
            RawPatentData(
                publication_ref=ref,
                country_code=ref[:2],
                doc_number=ref[2:-2],
                kind_code=ref[-2:],
            )
            for ref in _ALL_REFS
        ]

    async def fetch_bibliographic(self, pub_ref: str) -> dict:
        entry = _PATENTS.get(pub_ref.upper())
        if entry:
            return entry["biblio"]
        return {
            "publication_number": pub_ref,
            "title": pub_ref,
            "applicants": [],
            "inventors": [],
            "ipc_classes": [],
            "cpc_classes": [],
            "publication_date": "20200101",
            "priority_date": None,
        }

    async def fetch_abstract(self, pub_ref: str) -> str | None:
        entry = _PATENTS.get(pub_ref.upper())
        return entry["abstract"] if entry else None

    async def fetch_claims(self, pub_ref: str) -> str | None:
        entry = _PATENTS.get(pub_ref.upper())
        return entry["claims"] if entry else None

    async def fetch_legal_status(self, pub_ref: str) -> str:
        entry = _PATENTS.get(pub_ref.upper())
        return entry["legal_status"] if entry else "Unknown"

    async def fetch_family(self, pub_ref: str) -> list[str]:
        return []


mock_ops_connector = MockOpsConnector()
