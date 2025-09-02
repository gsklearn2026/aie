// Simple test to verify components can be imported
describe('ExportDashboard Components', () => {
  it('should import ExportDashboard without errors', () => {
    expect(() => {
      require('./ExportDashboard');
    }).not.toThrow();
  });

  it('should import ExportHistory without errors', () => {
    expect(() => {
      require('./ExportHistory');
    }).not.toThrow();
  });

  it('should import ExportProgress without errors', () => {
    expect(() => {
      require('./ExportProgress');
    }).not.toThrow();
  });

  it('should import ExportForm without errors', () => {
    expect(() => {
      require('./ExportForm');
    }).not.toThrow();
  });
});
