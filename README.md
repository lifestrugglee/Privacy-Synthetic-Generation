# Robust Privacy Amidst Innovation with Large Language Models Through a Critical Assessment of the Risks

<p align="center">
  <a href="https://github.com/lifestrugglee/Privacy-Synthetic-Generation/blob/master/LICENSE"><img src="https://img.shields.io/github/license/lifestrugglee/Privacy-Synthetic-Generation"></a>
  <a href="https://arxiv.org/abs/2407.16166"><img src="https://img.shields.io/badge/ARXIV-2407.16166-red"></a>
  <a href="https://academic.oup.com/jamia/article-abstract/32/5/885/8088353"><img src="https://img.shields.io/badge/JAMIA-2025-blue"></a>
  
</p>

## Description

In this work, we presents a novel method that enhances data privacy and interoperability in biomedical research by using advanced large language models (LLMs) to generate private, high-quality synthetic notes.

- Facilitates global collaboration with anonymized synthetic notes while maintaining patient data usability.
- Enhances trust, transparency, and security in patient data usage, encouraging participation in clinical research.
- Sets new ethical standards for AI in healthcare, representing a paradigm shift in patient privacy protection.


<img src="images/YSC_Figure1_Flowchart.jpg">

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Cite](#cite)

## Installation

#### 1. Data preparation
* The data used is from the MIMIC-III Clinical Database and is available under PhysioNet. Access to the data can be requested from PhysioNet. 
* The data preprocessing steps can be found at [GenerateEHRs](https://github.com/mominbuet/GenerateEHRs).
* ***Caution***: The GPT models' API utilized in this work is the HIPAA-compliant Azure OpenAI platform provided by UTHealth to ensure compliance with the data usage agreement requirements of MIMIC-III. More details could be found on the [PhysioNet annoucement](https://physionet.org/news/post/gpt-responsible-use).

#### 2. Python package
- Keyword extraction: 
`pip install requirements_keyword_extraction.txt`
- 

## Usage

1. Data Preparation

## Cite
```bibtex
@article{chuang2025robust,
  title={Robust privacy amidst innovation with large language models through a critical assessment of the risks},
  author={Chuang, Yao-Shun and Sarkar, Atiquer Rahman and Hsu, Yu-Chun and Mohammed, Noman and Jiang, Xiaoqian},
  journal={Journal of the American Medical Informatics Association},
  volume={32},
  number={5},
  pages={885--892},
  year={2025},
  publisher={Oxford University Press}
}
```
