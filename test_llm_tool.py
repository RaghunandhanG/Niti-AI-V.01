#!/usr/bin/env python3
"""
Test script to verify LLM tool integration
"""

import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()

@tool
def write_latex(latex_code: str) -> dict:
    """
    Write LaTeX code to the output.tex file.
    
    Args:
        latex_code (str): Complete LaTeX document code to write to file
        
    Returns:
        dict: Success status and file path
    """
    try:
        output_file = "output.tex"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(latex_code)
        
        return {
            "success": True,
            "message": f"LaTeX code successfully written to {output_file}",
            "output_file": os.path.abspath(output_file)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error writing LaTeX file: {str(e)}"
        }

def test_llm_tool_integration():
    """Test if LLM can use the write_latex tool"""
    print("🧪 Testing LLM Tool Integration...")
    
    # Initialize LLM
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY not found!")
        return False
    
    try:
        llm = ChatGroq(
            model="llama3-8b-8192",
            temperature=0.7,
            max_tokens=1000,
            api_key=api_key
        )
        
        # Bind tools
        llm_with_tools = llm.bind_tools([write_latex])
        print("✅ LLM initialized and tools bound")
        
        # Test message
        system_prompt = """You are a LaTeX resume generator. When asked to create a resume, you MUST use the write_latex tool to write complete LaTeX code to the output.tex file. Always use the tool when creating resumes."""
        
        test_message = "Create a simple resume for John Doe with email john@example.com, phone 123-456-7890, experience as Software Developer, and skills in Python and JavaScript."
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=test_message)
        ]
        
        print(f"📝 Sending test message: {test_message[:100]}...")
        
        # Get response
        response = llm_with_tools.invoke(messages)
        
        print(f"📄 Response type: {type(response)}")
        print(f"📝 Response content: {response.content[:200]}...")
        print(f"🔧 Has tool_calls: {hasattr(response, 'tool_calls')}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"📞 Tool calls made: {len(response.tool_calls)}")
            
            for i, tool_call in enumerate(response.tool_calls):
                print(f"   Tool {i+1}: {tool_call.get('name', 'Unknown')}")
                if tool_call.get('name') == 'write_latex':
                    latex_code = tool_call.get('args', {}).get('latex_code', '')
                    print(f"   LaTeX code length: {len(latex_code)} characters")
                    if latex_code:
                        print(f"   LaTeX preview: {latex_code[:150]}...")
                        
                        # Execute the tool
                        result = write_latex.invoke({'latex_code': latex_code})
                        print(f"   Tool execution result: {result}")
                        
                        if result['success']:
                            print("✅ Tool executed successfully!")
                            return True
                        else:
                            print(f"❌ Tool execution failed: {result['message']}")
                            return False
            
            print("✅ LLM made tool calls but not write_latex")
            return False
        else:
            print("❌ LLM did not make any tool calls")
            print("📝 Full response:")
            print(response.content)
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_llm_tool_integration()
    if success:
        print("\n✅ LLM Tool Integration Test PASSED!")
        print("🎉 The LLM can successfully use the write_latex tool")
    else:
        print("\n❌ LLM Tool Integration Test FAILED!")
        print("🔧 The LLM is not using the write_latex tool as expected")
        
    sys.exit(0 if success else 1) 