# ZeroRAG Memory Optimization Guide

This guide provides comprehensive information about memory management and optimization in ZeroRAG, including the recent improvements to handle high memory usage scenarios.

## Overview

ZeroRAG includes advanced memory management features to handle high memory usage scenarios efficiently. The system now includes:

- **Proactive Memory Monitoring**: Continuous monitoring with multiple threshold levels
- **Intelligent Cleanup Strategies**: Light, standard, and aggressive cleanup modes
- **Configurable Memory Thresholds**: Environment-based configuration for different deployment scenarios
- **Memory Optimization Tools**: Scripts and utilities for analysis and optimization

## Memory Management Architecture

### Memory Thresholds

The system uses three levels of memory monitoring:

1. **Preventive Threshold** (80% of main threshold): Triggers light cleanup
2. **Main Threshold** (default: 1000MB): Triggers standard cleanup
3. **Critical Threshold** (default: 1200MB): Triggers aggressive cleanup

### Cleanup Strategies

#### Light Cleanup
- Single garbage collection pass
- Clear old memory history entries
- Clear old performance alerts
- Minimal performance impact

#### Standard Cleanup
- Queued cleanup operations
- Background processing
- Moderate performance impact

#### Aggressive Cleanup
- Multiple garbage collection passes
- Clear most memory history
- Clear operation time history
- Force memory release
- Immediate execution

## Configuration

### Environment Variables

Add these to your `.env` file or environment:

```bash
# Memory Management
MEMORY_THRESHOLD_MB=1000
MEMORY_CRITICAL_THRESHOLD_MB=1200
GC_INTERVAL_SECONDS=180
BATCH_SIZE=100
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_THRESHOLD_MB` | 1000 | Memory threshold for cleanup (MB) |
| `MEMORY_CRITICAL_THRESHOLD_MB` | 1200 | Critical memory threshold (MB) |
| `GC_INTERVAL_SECONDS` | 180 | Garbage collection interval (seconds) |
| `BATCH_SIZE` | 100 | Default batch size for operations |

## Memory Optimization Tools

### Memory Analysis Script

```bash
# Generate comprehensive memory report
python scripts/optimize_memory.py --report

# Analyze current memory usage and get recommendations
python scripts/optimize_memory.py --analyze

# Perform memory cleanup
python scripts/optimize_memory.py --cleanup

# Perform aggressive memory cleanup
python scripts/optimize_memory.py --aggressive

# Monitor memory usage for 60 seconds
python scripts/optimize_memory.py --monitor 60

# Get optimization recommendations for 800MB target
python scripts/optimize_memory.py --optimize 800
```

### Debug Memory Usage Script

```bash
# Run comprehensive memory analysis
python debug_memory_usage.py
```

## Performance Monitoring

### Memory Alerts

The system generates performance alerts for memory issues:

- **Medium**: Memory usage approaching threshold
- **High**: Memory usage above main threshold
- **Critical**: Memory usage above critical threshold

### Health Status

Check memory health through the vector store service:

```python
from src.services.vector_store import VectorStoreService

vector_store = VectorStoreService()
health_status = vector_store.get_health_status()

print(f"Health Score: {health_status['health_score']}")
print(f"Memory Usage: {health_status['memory_usage']}")
print(f"Health Issues: {health_status['health_issues']}")
```

## Best Practices

### For Development

1. **Monitor Memory Usage**: Use the memory analysis tools regularly
2. **Set Appropriate Thresholds**: Adjust based on your system's capabilities
3. **Use Smaller Batch Sizes**: For memory-constrained environments
4. **Enable Aggressive Cleanup**: For long-running processes

### For Production

1. **Set Conservative Thresholds**: Leave headroom for system stability
2. **Monitor System Resources**: Ensure adequate RAM and swap space
3. **Use Memory Monitoring**: Implement alerts for memory issues
4. **Regular Cleanup**: Schedule periodic memory optimization

### For High-Load Scenarios

1. **Reduce Batch Sizes**: Use smaller batches to reduce memory spikes
2. **Increase GC Frequency**: More frequent garbage collection
3. **Enable Aggressive Monitoring**: Lower thresholds for early detection
4. **Use Memory Profiling**: Identify memory-intensive operations

## Troubleshooting

### High Memory Usage

**Symptoms:**
- Memory usage alerts
- Slow performance
- System instability

**Solutions:**
1. Run memory cleanup: `python scripts/optimize_memory.py --cleanup`
2. Check for memory leaks: `python debug_memory_usage.py`
3. Reduce batch sizes in configuration
4. Increase memory thresholds if system has adequate RAM

### Memory Leaks

**Symptoms:**
- Steadily increasing memory usage
- Memory not released after operations
- Performance degradation over time

**Solutions:**
1. Run aggressive cleanup: `python scripts/optimize_memory.py --aggressive`
2. Monitor memory trends: `python scripts/optimize_memory.py --monitor 300`
3. Check for circular references in code
4. Review large object creation patterns

### System Memory Pressure

**Symptoms:**
- High system memory usage
- Swap usage
- Overall system slowdown

**Solutions:**
1. Close unnecessary applications
2. Increase system RAM if possible
3. Optimize ZeroRAG memory settings
4. Use memory-efficient operations

## Configuration Examples

### Low Memory Environment (4GB RAM)

```bash
MEMORY_THRESHOLD_MB=600
MEMORY_CRITICAL_THRESHOLD_MB=800
BATCH_SIZE=50
GC_INTERVAL_SECONDS=120
```

### Standard Environment (8GB RAM)

```bash
MEMORY_THRESHOLD_MB=1000
MEMORY_CRITICAL_THRESHOLD_MB=1200
BATCH_SIZE=100
GC_INTERVAL_SECONDS=180
```

### High Memory Environment (16GB+ RAM)

```bash
MEMORY_THRESHOLD_MB=1200
MEMORY_CRITICAL_THRESHOLD_MB=1500
BATCH_SIZE=150
GC_INTERVAL_SECONDS=300
```

## Monitoring and Alerts

### Performance Alerts

The system automatically generates alerts for:

- Memory usage above thresholds
- Slow operations
- High error rates
- Queue overflow

### Health Monitoring

Regular health checks include:

- Memory usage metrics
- Operation performance
- Error rates
- Background service status

### Logging

Memory-related logs include:

- Memory cleanup events
- Performance alerts
- Memory usage trends
- Cleanup operation results

## Recent Improvements

### Enhanced Memory Monitoring

- **Multiple Threshold Levels**: Preventive, main, and critical thresholds
- **Proactive Cleanup**: Light cleanup before reaching main threshold
- **Immediate Response**: Aggressive cleanup for critical situations

### Improved Batch Processing

- **Memory-Aware Chunking**: Smaller chunks with memory checks
- **Progressive Cleanup**: Memory cleanup during batch operations
- **Resource Management**: Better memory release after operations

### Configuration Flexibility

- **Environment-Based**: All memory settings configurable via environment variables
- **Runtime Adjustment**: Settings can be changed without restart
- **System-Aware**: Automatic recommendations based on system capabilities

## Future Enhancements

### Planned Features

1. **Memory Pooling**: Reuse memory objects for better efficiency
2. **Predictive Cleanup**: Anticipate memory needs and clean proactively
3. **Memory Profiling**: Detailed analysis of memory usage patterns
4. **Adaptive Thresholds**: Dynamic threshold adjustment based on usage patterns

### Performance Optimizations

1. **Lazy Loading**: Load data only when needed
2. **Memory Compression**: Compress data in memory
3. **Cache Management**: Intelligent cache sizing and eviction
4. **Background Optimization**: Continuous memory optimization

## Support and Resources

### Getting Help

- Check the memory optimization tools for diagnostics
- Review system resources and configuration
- Monitor memory usage patterns over time
- Consult the performance monitoring logs

### Additional Resources

- [ZeroRAG Configuration Guide](configuration.md)
- [Performance Monitoring Guide](performance_monitoring.md)
- [Troubleshooting Guide](troubleshooting.md)
- [API Documentation](api_documentation.md)

---

*This guide covers the memory optimization features added to handle the high memory usage scenario you experienced. The system now provides proactive monitoring, intelligent cleanup strategies, and comprehensive tools for memory management.*
