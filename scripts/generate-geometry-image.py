#!/usr/bin/env python3
"""
幾何圖形自動生成工具
用於為數學題目生成圖片
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Songti SC', 'STHeiti']
plt.rcParams['axes.unicode_minus'] = False

class GeometryGenerator:
    """幾何圖形生成器"""
    
    def __init__(self, output_dir='exams/images'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def draw_triangle(self, base=8, height=6, filename='triangle.png'):
        """繪製三角形"""
        fig, ax = plt.subplots(figsize=(6, 5))
        
        # 三角形頂點
        triangle = patches.Polygon(
            [(0, 0), (base, 0), (base/2, height)],
            closed=True,
            edgecolor='black',
            facecolor='lightblue',
            linewidth=2
        )
        ax.add_patch(triangle)
        
        # 標註
        ax.text(base/2, -0.5, f'{base} cm', ha='center', fontsize=12)
        ax.text(-0.5, height/2, f'{height} cm', rotation=90, va='center', fontsize=12)
        ax.text(base/2, height+0.3, 'A', ha='center', fontsize=14, fontweight='bold')
        ax.text(-0.3, -0.3, 'B', fontsize=14, fontweight='bold')
        ax.text(base+0.3, -0.3, 'C', fontsize=14, fontweight='bold')
        
        ax.set_xlim(-1, base+1)
        ax.set_ylim(-1, height+1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ 已生成：{output_path}')
        return output_path
    
    def draw_rectangle(self, width=12, height=8, filename='rectangle.png'):
        """繪製長方形"""
        fig, ax = plt.subplots(figsize=(7, 5))
        
        rectangle = patches.Rectangle(
            (0, 0), width, height,
            edgecolor='black',
            facecolor='lightgreen',
            linewidth=2
        )
        ax.add_patch(rectangle)
        
        # 對角線
        ax.plot([0, width], [0, height], 'r--', linewidth=1.5, label='對角線 AC')
        
        # 標註
        ax.text(width/2, -0.8, f'{width} cm', ha='center', fontsize=12)
        ax.text(-0.8, height/2, f'{height} cm', rotation=90, va='center', fontsize=12)
        ax.text(-0.5, -0.5, 'A', fontsize=14, fontweight='bold')
        ax.text(width+0.5, -0.5, 'B', fontsize=14, fontweight='bold')
        ax.text(width+0.5, height+0.5, 'C', fontsize=14, fontweight='bold')
        ax.text(-0.5, height+0.5, 'D', fontsize=14, fontweight='bold')
        
        ax.set_xlim(-2, width+2)
        ax.set_ylim(-2, height+2)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.legend(loc='upper right')
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ 已生成：{output_path}')
        return output_path
    
    def draw_circle(self, radius=5, filename='circle.png', sector_angle=None):
        """繪製圓形或扇形"""
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # 圓形
        circle = patches.Circle(
            (0, 0), radius,
            edgecolor='black',
            facecolor='lightyellow',
            linewidth=2
        )
        ax.add_patch(circle)
        
        # 如果有扇形角度
        if sector_angle:
            sector = patches.Wedge(
                (0, 0), radius, 0, sector_angle,
                edgecolor='red',
                facecolor='lightcoral',
                linewidth=2,
                alpha=0.7
            )
            ax.add_patch(sector)
            ax.text(radius/2, 0.3, f'{sector_angle}°', fontsize=12, color='red')
        
        # 半徑線
        ax.plot([0, radius], [0, 0], 'b-', linewidth=1.5)
        ax.text(radius/2, -0.5, f'r = {radius} cm', ha='center', fontsize=12, color='blue')
        
        # 圓心
        ax.plot(0, 0, 'ko', markersize=8)
        ax.text(0.3, 0.3, 'O', fontsize=14, fontweight='bold')
        
        ax.set_xlim(-radius-2, radius+2)
        ax.set_ylim(-radius-2, radius+2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ 已生成：{output_path}')
        return output_path
    
    def draw_coordinate_plane(self, points=None, filename='coordinate.png'):
        """繪製座標平面"""
        fig, ax = plt.subplots(figsize=(7, 7))
        
        # 座標軸
        ax.axhline(y=0, color='k', linewidth=1)
        ax.axvline(x=0, color='k', linewidth=1)
        ax.grid(True, alpha=0.3)
        
        # 標註
        ax.set_xlabel('x', fontsize=14, loc='right')
        ax.set_ylabel('y', fontsize=14, loc='top')
        
        # 繪製點
        if points:
            for name, (x, y) in points.items():
                ax.plot(x, y, 'ro', markersize=10)
                ax.text(x+0.3, y+0.3, f'{name}({x},{y})', fontsize=12, fontweight='bold')
        
        ax.set_xlim(-1, 6)
        ax.set_ylim(-1, 6)
        ax.set_aspect('equal')
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ 已生成：{output_path}')
        return output_path
    
    def draw_bar_chart(self, data, filename='bar_chart.png'):
        """繪製長條圖"""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        categories = list(data.keys())
        values = list(data.values())
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        
        bars = ax.bar(categories, values, color=colors[:len(categories)], edgecolor='black', linewidth=1.5)
        
        # 在每個長條上標註數值
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('人數', fontsize=12)
        ax.set_xlabel('次數範圍', fontsize=12)
        ax.set_title('跳繩測驗成績分布', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ 已生成：{output_path}')
        return output_path
    
    def draw_composite_shape(self, filename='composite.png'):
        """繪製複合圖形（正方形+半圓）"""
        fig, ax = plt.subplots(figsize=(6, 7))
        
        side = 10
        
        # 正方形
        rectangle = patches.Rectangle(
            (0, 0), side, side,
            edgecolor='black',
            facecolor='lightblue',
            linewidth=2
        )
        ax.add_patch(rectangle)
        
        # 半圓
        semicircle = patches.Wedge(
            (side/2, side), side/2, 0, 180,
            edgecolor='black',
            facecolor='lightcoral',
            linewidth=2
        )
        ax.add_patch(semicircle)
        
        # 標註
        ax.text(side/2, -1, f'{side} cm', ha='center', fontsize=12)
        ax.text(-1, side/2, f'{side} cm', rotation=90, va='center', fontsize=12)
        ax.text(side/2, side+side/4+0.5, f'半圓直徑 = {side} cm', ha='center', fontsize=11, color='red')
        
        ax.set_xlim(-2, side+2)
        ax.set_ylim(-2, side+side/2+2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ 已生成：{output_path}')
        return output_path


def main():
    """示範使用"""
    print('🎨 幾何圖形生成器')
    print('='*50)
    
    gen = GeometryGenerator()
    
    # 生成各種圖形
    gen.draw_triangle(base=8, height=6, filename='triangle-demo.png')
    gen.draw_rectangle(width=12, height=8, filename='rectangle-demo.png')
    gen.draw_circle(radius=5, filename='circle-demo.png')
    gen.draw_circle(radius=5, sector_angle=90, filename='sector-demo.png')
    gen.draw_coordinate_plane(
        points={'A': (1, 2), 'B': (3, 5)},
        filename='coordinate-demo.png'
    )
    gen.draw_bar_chart(
        {'0-20': 3, '21-40': 5, '41-60': 10, '61-80': 7, '81-100': 5},
        filename='bar-chart-demo.png'
    )
    gen.draw_composite_shape(filename='composite-demo.png')
    
    print('='*50)
    print('✅ 所有圖形已生成完畢！')
    print(f'📁 輸出目錄：{gen.output_dir.absolute()}')


if __name__ == '__main__':
    main()
