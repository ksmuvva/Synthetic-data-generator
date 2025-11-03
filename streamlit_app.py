"""
Streamlit Frontend for Synthetic Data Generator

This app provides a user-friendly web interface for:
- Adding prompts for data generation
- Uploading documents, PDFs, and various file formats for pattern analysis
- Configuring generation settings
- Previewing and exporting generated data
"""

import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path
from datetime import datetime
import json
import tempfile

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from synth_agent.core.config import ConfigManager
from synth_agent.generation.engine import DataGenerationEngine
from synth_agent.analysis.pattern_analyzer import PatternAnalyzer
from synth_agent.analysis.requirement_parser import RequirementParser
from synth_agent.formats.manager import FormatManager
from synth_agent.llm.manager import LLMManager
from synth_agent.llm.anthropic_provider import AnthropicProvider
from synth_agent.utils.file_validator import FileValidator
from synth_agent.validation.quality import QualityValidator

# Page configuration
st.set_page_config(
    page_title="Synthetic Data Generator",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #0c5460;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "prompt_history" not in st.session_state:
    st.session_state.prompt_history = []
if "generated_data" not in st.session_state:
    st.session_state.generated_data = None
if "pattern_analysis" not in st.session_state:
    st.session_state.pattern_analysis = None
if "uploaded_file_path" not in st.session_state:
    st.session_state.uploaded_file_path = None
if "generation_config" not in st.session_state:
    st.session_state.generation_config = {}

def initialize_components():
    """Initialize the core components for data generation."""
    try:
        config_manager = ConfigManager()
        config = config_manager.get_config()

        # Get API keys from environment
        from synth_agent.core.config import get_api_keys
        api_keys = get_api_keys()

        if not api_keys.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        # Initialize LLM provider with API key
        llm_provider = AnthropicProvider(
            api_key=api_keys.anthropic_api_key,
            model=config.llm.model,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            timeout=config.llm.timeout
        )
        llm_manager = LLMManager(provider=llm_provider, config=config.llm)

        # Initialize other components
        requirement_parser = RequirementParser(llm_manager=llm_manager)
        pattern_analyzer = PatternAnalyzer(llm_manager=llm_manager, config=config)
        generation_engine = DataGenerationEngine(config=config.generation)
        format_manager = FormatManager()
        quality_validator = QualityValidator()
        file_validator = FileValidator()

        return {
            "config": config,
            "requirement_parser": requirement_parser,
            "pattern_analyzer": pattern_analyzer,
            "generation_engine": generation_engine,
            "format_manager": format_manager,
            "quality_validator": quality_validator,
            "file_validator": file_validator
        }
    except Exception as e:
        st.error(f"Failed to initialize components: {str(e)}")
        st.info("Please ensure your API keys are set in environment variables (ANTHROPIC_API_KEY or OPENAI_API_KEY)")
        return None

def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary directory."""
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

def analyze_uploaded_file(file_path, components):
    """Analyze uploaded file for patterns."""
    try:
        with st.spinner("Analyzing file patterns..."):
            # Validate file first
            validation_result = components["file_validator"].validate_file(file_path)

            if not validation_result["is_valid"]:
                st.error(f"File validation failed: {validation_result.get('error', 'Unknown error')}")
                return None

            # Perform pattern analysis
            analysis = components["pattern_analyzer"].analyze(file_path)

            return analysis
    except Exception as e:
        st.error(f"Error analyzing file: {str(e)}")
        return None

def parse_user_prompt(prompt, components):
    """Parse user prompt into requirements."""
    try:
        with st.spinner("Understanding your requirements..."):
            requirements = components["requirement_parser"].parse(prompt)
            return requirements
    except Exception as e:
        st.error(f"Error parsing prompt: {str(e)}")
        return None

def generate_synthetic_data(requirements, pattern_analysis, components, num_rows):
    """Generate synthetic data based on requirements and patterns."""
    try:
        with st.spinner(f"Generating {num_rows} rows of synthetic data..."):
            # If we have pattern analysis, use it as template
            template_df = None
            if pattern_analysis and "data" in pattern_analysis:
                template_df = pattern_analysis["data"]

            # Generate data
            generated_df = components["generation_engine"].generate(
                requirements=requirements,
                num_rows=num_rows,
                template_df=template_df
            )

            return generated_df
    except Exception as e:
        st.error(f"Error generating data: {str(e)}")
        return None

def main():
    """Main Streamlit application."""

    # Header
    st.markdown('<div class="main-header">🔮 Synthetic Data Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Data Generation with Pattern Learning</div>', unsafe_allow_html=True)

    # Initialize components
    components = initialize_components()

    if components is None:
        st.stop()

    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Generation settings
        st.subheader("Generation Settings")
        num_rows = st.slider(
            "Number of Rows",
            min_value=10,
            max_value=10000,
            value=100,
            step=10,
            help="Number of rows to generate"
        )

        quality_level = st.selectbox(
            "Quality Level",
            options=["low", "medium", "high"],
            index=1,
            help="Higher quality takes longer but produces better results"
        )

        generation_mode = st.selectbox(
            "Generation Mode",
            options=["balanced", "exact_match", "realistic_variant", "edge_case"],
            index=0,
            help="Controls the distribution and variance of generated data"
        )

        # Export settings
        st.subheader("Export Settings")
        export_format = st.selectbox(
            "Export Format",
            options=["csv", "json", "excel", "parquet", "xml", "sql"],
            index=0,
            help="Format for exporting generated data"
        )

        # Store config in session state
        st.session_state.generation_config = {
            "num_rows": num_rows,
            "quality_level": quality_level,
            "generation_mode": generation_mode,
            "export_format": export_format
        }

        # Help section
        st.divider()
        st.subheader("📚 Help")
        st.markdown("""
        **How to use:**
        1. Enter a prompt describing the data you need
        2. Optionally upload a template file
        3. Configure generation settings
        4. Click Generate to create data
        5. Preview and export results
        """)

        # Display prompt history
        if st.session_state.prompt_history:
            st.divider()
            st.subheader("📝 Recent Prompts")
            for i, prompt in enumerate(reversed(st.session_state.prompt_history[-5:])):
                with st.expander(f"Prompt {len(st.session_state.prompt_history) - i}"):
                    st.text(prompt[:100] + "..." if len(prompt) > 100 else prompt)

    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["📝 Prompt Input", "📁 File Upload", "📊 Generated Data"])

    # Tab 1: Prompt Input
    with tab1:
        st.header("Enter Your Data Generation Prompt")
        st.markdown("Describe the data you want to generate in natural language.")

        # Examples
        with st.expander("💡 Example Prompts"):
            st.markdown("""
            - "Generate customer data with names, emails, phone numbers, and addresses"
            - "Create a dataset of 500 transactions with dates, amounts, and categories"
            - "Generate employee records with ID, name, department, salary, and hire date"
            - "Create product inventory with SKU, name, price, quantity, and supplier"
            """)

        # Prompt input
        user_prompt = st.text_area(
            "Your Prompt",
            height=150,
            placeholder="Example: Generate 100 customer records with names, email addresses, phone numbers, and registration dates...",
            help="Describe what kind of data you want to generate"
        )

        col1, col2 = st.columns([1, 3])
        with col1:
            generate_from_prompt = st.button("🚀 Generate Data", type="primary", use_container_width=True)
        with col2:
            if user_prompt:
                st.info(f"Will generate {num_rows} rows")

        if generate_from_prompt and user_prompt:
            # Add to history
            st.session_state.prompt_history.append(user_prompt)

            # Parse requirements
            requirements = parse_user_prompt(user_prompt, components)

            if requirements:
                st.success("✅ Requirements understood!")

                # Show parsed requirements
                with st.expander("Parsed Requirements"):
                    st.json(requirements if isinstance(requirements, dict) else str(requirements))

                # Generate data
                generated_df = generate_synthetic_data(
                    requirements,
                    st.session_state.pattern_analysis,
                    components,
                    st.session_state.generation_config["num_rows"]
                )

                if generated_df is not None and not generated_df.empty:
                    st.session_state.generated_data = generated_df
                    st.success(f"✅ Generated {len(generated_df)} rows successfully!")
                    st.balloons()

                    # Switch to results tab
                    st.info("👉 Check the 'Generated Data' tab to view and export your data!")

    # Tab 2: File Upload
    with tab2:
        st.header("Upload Template or Sample Data")
        st.markdown("Upload a file to analyze patterns and generate similar data.")

        # Supported formats info
        with st.expander("📋 Supported File Formats"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **Data Files:**
                - CSV (.csv)
                - JSON (.json)
                - Excel (.xlsx, .xls)
                - Parquet (.parquet)
                """)
            with col2:
                st.markdown("""
                **Document Files:**
                - PDF (.pdf)
                - Text (.txt)
                - Markdown (.md)
                """)

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "json", "xlsx", "xls", "parquet", "pdf", "txt", "md"],
            help="Upload a template file for pattern analysis"
        )

        if uploaded_file is not None:
            # Display file info
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Name", uploaded_file.name)
            with col2:
                st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
            with col3:
                st.metric("File Type", uploaded_file.type)
            st.markdown('</div>', unsafe_allow_html=True)

            # Save and analyze file
            if st.button("🔍 Analyze File", type="primary", use_container_width=True):
                file_path = save_uploaded_file(uploaded_file)

                if file_path:
                    st.session_state.uploaded_file_path = file_path

                    # Analyze the file
                    analysis = analyze_uploaded_file(file_path, components)

                    if analysis:
                        st.session_state.pattern_analysis = analysis
                        st.success("✅ File analyzed successfully!")

                        # Display analysis results
                        st.subheader("Pattern Analysis Results")

                        # Show data preview if available
                        if "data" in analysis and analysis["data"] is not None:
                            st.write("**Data Preview:**")
                            st.dataframe(analysis["data"].head(10), use_container_width=True)

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Rows", len(analysis["data"]))
                            with col2:
                                st.metric("Columns", len(analysis["data"].columns))
                            with col3:
                                st.metric("Data Types", analysis["data"].dtypes.nunique())

                        # Show analysis insights
                        if "analysis" in analysis:
                            with st.expander("📊 Detailed Analysis", expanded=True):
                                st.json(analysis["analysis"])

                        st.info("💡 You can now generate data based on this pattern!")

            # Generate from uploaded pattern
            if st.session_state.pattern_analysis and st.button("🚀 Generate from Pattern", use_container_width=True):
                # Generate data using the pattern
                generated_df = generate_synthetic_data(
                    None,
                    st.session_state.pattern_analysis,
                    components,
                    st.session_state.generation_config["num_rows"]
                )

                if generated_df is not None and not generated_df.empty:
                    st.session_state.generated_data = generated_df
                    st.success(f"✅ Generated {len(generated_df)} rows based on pattern!")
                    st.balloons()
                    st.info("👉 Check the 'Generated Data' tab to view and export your data!")

    # Tab 3: Generated Data
    with tab3:
        st.header("Generated Data Preview & Export")

        if st.session_state.generated_data is not None:
            df = st.session_state.generated_data

            # Summary metrics
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Total Columns", len(df.columns))
            with col3:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
            with col4:
                st.metric("Generated", datetime.now().strftime("%H:%M:%S"))
            st.markdown('</div>', unsafe_allow_html=True)

            # Data preview
            st.subheader("Data Preview")

            # Search/filter
            search_col = st.selectbox("Search in column", ["All"] + list(df.columns))
            search_term = st.text_input("Search term")

            display_df = df
            if search_term and search_col != "All":
                display_df = df[df[search_col].astype(str).str.contains(search_term, case=False, na=False)]
            elif search_term:
                # Search in all columns
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                display_df = df[mask]

            st.dataframe(display_df, use_container_width=True, height=400)

            # Column statistics
            st.subheader("Column Statistics")
            selected_columns = st.multiselect(
                "Select columns for statistics",
                options=list(df.columns),
                default=list(df.columns)[:3] if len(df.columns) >= 3 else list(df.columns)
            )

            if selected_columns:
                stats_df = df[selected_columns].describe()
                st.dataframe(stats_df, use_container_width=True)

            # Export functionality
            st.subheader("Export Data")

            export_format = st.session_state.generation_config["export_format"]

            col1, col2 = st.columns([2, 1])
            with col1:
                output_filename = st.text_input(
                    "Output filename",
                    value=f"synthetic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
            with col2:
                st.info(f"Format: {export_format.upper()}")

            if st.button("💾 Export Data", type="primary", use_container_width=True):
                try:
                    output_dir = Path("./output")
                    output_dir.mkdir(exist_ok=True)

                    output_path = output_dir / f"{output_filename}.{export_format}"

                    # Export using format manager
                    with st.spinner(f"Exporting to {export_format.upper()}..."):
                        if export_format == "csv":
                            df.to_csv(output_path, index=False)
                        elif export_format == "json":
                            df.to_json(output_path, orient="records", indent=2)
                        elif export_format == "excel":
                            df.to_excel(output_path, index=False, engine="openpyxl")
                        elif export_format == "parquet":
                            df.to_parquet(output_path, index=False)
                        elif export_format == "xml":
                            df.to_xml(output_path, index=False)
                        elif export_format == "sql":
                            with open(output_path, "w") as f:
                                for _, row in df.iterrows():
                                    values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in row])
                                    f.write(f"INSERT INTO data VALUES ({values});\n")

                    st.success(f"✅ Data exported to: {output_path}")

                    # Provide download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download File",
                            data=f,
                            file_name=f"{output_filename}.{export_format}",
                            mime="application/octet-stream"
                        )

                except Exception as e:
                    st.error(f"Error exporting data: {str(e)}")
        else:
            st.info("👈 Generate data using the 'Prompt Input' or 'File Upload' tabs first!")

            # Show placeholder example
            st.markdown("### Example Output")
            example_df = pd.DataFrame({
                "ID": [1, 2, 3],
                "Name": ["John Doe", "Jane Smith", "Bob Johnson"],
                "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
                "Age": [28, 34, 45]
            })
            st.dataframe(example_df, use_container_width=True)

if __name__ == "__main__":
    main()
