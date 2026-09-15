from typing import Dict, List

from rapidfuzz import fuzz

SKILL_ALIASES: Dict[str, str] = {

    # Programming Languages
    'py': 'python',
    'python3': 'python',
    'python 3': 'python',
    'js': 'javascript',
    'javascript es6': 'javascript',
    'ecmascript': 'javascript',
    'ts': 'typescript',
    'c++': 'cpp',
    'c plus plus': 'cpp',
    'c#': 'csharp',
    'c sharp': 'csharp',
    'golang': 'go',
    'rb': 'ruby',
    'ruby on rails': 'rails',
    'objective c': 'objective-c',
    'shell scripting': 'shell',
    'bash scripting': 'bash',

    # Frontend
    'reactjs': 'react',
    'react.js': 'react',
    'react js': 'react',
    'angularjs': 'angular',
    'angular.js': 'angular',
    'angular js': 'angular',
    'vuejs': 'vue',
    'vue.js': 'vue',
    'vue js': 'vue',
    'nextjs': 'next.js',
    'next js': 'next.js',
    'nuxtjs': 'nuxt.js',
    'sveltejs': 'svelte',
    'html5': 'html',
    'css3': 'css',
    'tailwindcss': 'tailwind',
    'tailwind css': 'tailwind',
    'bootstrap5': 'bootstrap',
    'bootstrap 5': 'bootstrap',

    # Backend
    'nodejs': 'node.js',
    'node js': 'node.js',
    'node': 'node.js',
    'expressjs': 'express',
    'express.js': 'express',
    'express js': 'express',
    'springboot': 'spring boot',
    'spring-boot': 'spring boot',
    'fast api': 'fastapi',
    'asp.net': '.net',
    'asp net': '.net',
    'dotnet': '.net',
    '.net core': '.net',
    'drf': 'django rest framework',

    # Databases
    'postgres': 'postgresql',
    'postgres db': 'postgresql',
    'postgres database': 'postgresql',
    'mysql db': 'mysql',
    'mysql database': 'mysql',
    'mongo': 'mongodb',
    'mongo db': 'mongodb',
    'mssql': 'sql server',
    'ms sql': 'sql server',
    'microsoft sql server': 'sql server',
    'redis db': 'redis',

    # Cloud
    'amazon web services': 'aws',
    'amazon aws': 'aws',
    'aws cloud': 'aws',
    'google cloud': 'gcp',
    'google cloud platform': 'gcp',
    'microsoft azure': 'azure',
    'ms azure': 'azure',

    # DevOps
    'docker-compose': 'docker compose',
    'docker compose': 'docker compose',
    'k8s': 'kubernetes',
    'kubernetes cluster': 'kubernetes',
    'ci/cd': 'cicd',
    'ci cd': 'cicd',
    'continuous integration': 'cicd',
    'continuous deployment': 'cicd',
    'gitlab ci': 'gitlab ci',
    'jenkins ci': 'jenkins',
    'iac': 'infrastructure as code',

    # Data Science / ML
    'ml': 'machine learning',
    'machine-learning': 'machine learning',
    'ai': 'artificial intelligence',
    'artificial-intelligence': 'artificial intelligence',
    'dl': 'deep learning',
    'deep-learning': 'deep learning',
    'nlp': 'natural language processing',
    'natural-language-processing': 'natural language processing',
    'cv': 'computer vision',
    'computer-vision': 'computer vision',
    'sklearn': 'scikit-learn',
    'scikit learn': 'scikit-learn',
    'tf': 'tensorflow',
    'tensorflow 2': 'tensorflow',
    'torch': 'pytorch',
    'py torch': 'pytorch',
    'xgb': 'xgboost',
    'lgbm': 'lightgbm',
    'light gbm': 'lightgbm',
    'cat boost': 'catboost',

    # NLP / LLM / Generative AI
    'large language model': 'llm',
    'large language models': 'llm',
    'large-language-model': 'llm',
    'gen ai': 'generative ai',
    'genai': 'generative ai',
    'generative artificial intelligence': 'generative ai',
    'rag': 'retrieval augmented generation',
    'retrieval-augmented generation': 'retrieval augmented generation',
    'lang chain': 'langchain',
    'lang-chain': 'langchain',
    'lang graph': 'langgraph',
    'lang-graph': 'langgraph',
    'open ai': 'openai',
    'open-ai': 'openai',
    'chat gpt': 'chatgpt',
    'chat-gpt': 'chatgpt',
    'huggingface': 'hugging face',
    'hugging-face': 'hugging face',
    'hf transformers': 'transformers',
    'transformer models': 'transformers',

    # Big Data
    'pyspark': 'spark',
    'apache spark': 'spark',
    'spark sql': 'spark',
    'hdfs': 'hadoop',
    'apache kafka': 'kafka',

    # Data Analytics / BI
    'powerbi': 'power bi',
    'power-bi': 'power bi',
    'microsoft power bi': 'power bi',
    'tableau desktop': 'tableau',
    'ms excel': 'excel',
    'microsoft excel': 'excel',
    'excel advanced': 'excel',

    # Python Data Stack
    'np': 'numpy',
    'pd': 'pandas',
    'matplotlib pyplot': 'matplotlib',
    'sns': 'seaborn',
    'plotly express': 'plotly',

    # APIs / Web
    'rest api': 'rest',
    'restful api': 'rest',
    'restful apis': 'rest',
    'graphql api': 'graphql',
    'websocket': 'websockets',
    'web sockets': 'websockets',

    # Version Control
    'git hub': 'github',
    'git-hub': 'github',
    'git lab': 'gitlab',
    'git-lab': 'gitlab',
    'version control': 'git',

    # Operating Systems
    'linux os': 'linux',
    'gnu/linux': 'linux',

    # Cybersecurity
    'cyber security': 'cybersecurity',
    'cyber-security': 'cybersecurity',
    'infosec': 'information security',
    'pentesting': 'penetration testing',
    'pen testing': 'penetration testing',
    'ethical hacking': 'ethical hacking',
    'iam': 'identity and access management',

    # Software Engineering
    'oop': 'object oriented programming',
    'object-oriented programming': 'object oriented programming',
    'object oriented design': 'object oriented design',
    'dsa': 'data structures and algorithms',
    'data structures & algorithms': 'data structures and algorithms',
    'unit testing': 'testing',
    'automated testing': 'testing',

    # Java Ecosystem
    'jdk': 'java',
    'java ee': 'jakarta ee',
    'java enterprise edition': 'jakarta ee',
    'maven build': 'maven',
    'apache maven': 'maven',
    'gradle build': 'gradle',

    # Deployment / Tools
    'vercel app': 'vercel',
    'netlify app': 'netlify',
    'heroku app': 'heroku',
    'postman api': 'postman',

    # Common ATS Terms
    'sql queries': 'sql',
    'structured query language': 'sql',
    'machine learning engineer': 'machine learning',
    'ml engineer': 'machine learning',
    'data scientist': 'data science',
    'software developer': 'software development',
    'software engineer': 'software engineering',
}
def normalize_skill(skill: str) -> str:
    cleaned = skill.strip().lower()
    return SKILL_ALIASES.get(cleaned, cleaned)

def fuzzy_match_keywords(
    resume_keywords: List[str],
    jd_keywords: List[str],
    threshold: int = 80,
) -> Dict[str, List[str]]:
    resume_normalized = {normalize_skill(kw): kw for kw in resume_keywords}
    jd_normalized = {normalize_skill(kw): kw for kw in jd_keywords}
    
    matched_jd_originals = []
    missing_jd_originals = []
    
    
    for jd_canon, jd_original in jd_normalized.items():
        # 1. Exact cannonical match
        if jd_canon in resume_normalized:
            matched_jd_originals.append(jd_original)
            continue
        
        # 2. Fuzzy match against all resume cannonical names
        best_scores = 0
        for resume_canon in resume_normalized:
            score = fuzz.token_sort_ratio(jd_canon, resume_canon)
            best_score = max(best_score, score)
            
        if best_score >= threshold:
            matched_jd_originals.append(jd_original)
        else:
            missing_jd_originals.append(jd_original)
            
    return{
        'matched': sorted(matched_jd_originals),
        'missing': missing_jd_originals,
    }
            
            