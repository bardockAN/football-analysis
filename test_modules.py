"""
Script test nhanh để kiểm tra các module mới
"""

print("Testing Case Studies and Analytics Modules...")
print("=" * 60)

try:
    # Test imports
    print("\n1. Testing imports...")
    from case_studies import TeamComparisonAnalyzer, MVPAnalyzer, TacticalAnalyzer
    from analytics import DataExporter, DashboardGenerator, ReportGenerator
    print("   ✓ All imports successful!")
    
    # Test TeamComparisonAnalyzer
    print("\n2. Testing TeamComparisonAnalyzer...")
    team_analyzer = TeamComparisonAnalyzer()
    print("   ✓ TeamComparisonAnalyzer initialized")
    
    # Test MVPAnalyzer
    print("\n3. Testing MVPAnalyzer...")
    mvp_analyzer = MVPAnalyzer()
    print("   ✓ MVPAnalyzer initialized")
    
    # Test TacticalAnalyzer
    print("\n4. Testing TacticalAnalyzer...")
    tactical_analyzer = TacticalAnalyzer()
    print("   ✓ TacticalAnalyzer initialized")
    
    # Test DataExporter
    print("\n5. Testing DataExporter...")
    data_exporter = DataExporter()
    print("   ✓ DataExporter initialized")
    
    # Test DashboardGenerator
    print("\n6. Testing DashboardGenerator...")
    dashboard_gen = DashboardGenerator()
    print("   ✓ DashboardGenerator initialized")
    
    # Test ReportGenerator
    print("\n7. Testing ReportGenerator...")
    report_gen = ReportGenerator()
    print("   ✓ ReportGenerator initialized")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nBạn có thể chạy: python main.py")
    print("để thực hiện phân tích đầy đủ với tất cả case studies!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
