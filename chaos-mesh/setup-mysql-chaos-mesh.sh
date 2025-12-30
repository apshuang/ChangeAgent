#!/bin/bash
# MySQL 和 Chaos-Mesh 一键安装脚本
# 使用方法: ./setup-mysql-chaos-mesh.sh

set -e

NAMESPACE="chaos-mesh"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYSQL_HOST="10.10.1.202"
MYSQL_PORT="3306"
MYSQL_USER="root"
MYSQL_PASSWORD="elastic"
MYSQL_DATABASE="chaos_mesh"
CHAOS_MESH_VERSION="2.5.1"
# NodePort 端口配置（范围：30000-32767）
DASHBOARD_NODEPORT_HTTP="31441"
DASHBOARD_NODEPORT_METRIC="31614"

echo "=========================================="
echo "MySQL 和 Chaos-Mesh 配置脚本"
echo "=========================================="
echo ""

# 检查 helm 是否安装
if ! command -v helm &> /dev/null; then
    echo "错误: helm 未安装，请先安装 helm"
    exit 1
fi

# 检查 kubectl 是否安装
if ! command -v kubectl &> /dev/null; then
    echo "错误: kubectl 未安装，请先安装 kubectl"
    exit 1
fi

# 步骤 0: 安装 Chaos Mesh
echo "步骤 0/7: 安装 Chaos Mesh..."
echo ""

# 添加 helm repo
if ! helm repo list | grep -q chaos-mesh; then
    echo "添加 Chaos Mesh Helm 仓库..."
    helm repo add chaos-mesh https://charts.chaos-mesh.org
    helm repo update
    echo "✓ Chaos Mesh Helm 仓库已添加"
else
    echo "✓ Chaos Mesh Helm 仓库已存在"
fi
echo ""

# 创建命名空间（如果不存在）
if ! kubectl get namespace "$NAMESPACE" &>/dev/null; then
    echo "创建命名空间 $NAMESPACE..."
    kubectl create ns "$NAMESPACE"
    echo "✓ 命名空间 $NAMESPACE 已创建"
else
    echo "✓ 命名空间 $NAMESPACE 已存在"
fi
echo ""

# 检查 Chaos Mesh 是否已安装
CHAOS_MESH_INSTALLED=false
if helm list -n "$NAMESPACE" | grep -q chaos-mesh; then
    echo "✓ Chaos Mesh 已安装，跳过安装步骤"
    CHAOS_MESH_INSTALLED=true
else
    echo "安装 Chaos Mesh..."
    helm install chaos-mesh chaos-mesh/chaos-mesh -n "$NAMESPACE" \
        --version="$CHAOS_MESH_VERSION" \
        --set "dashboard.env.DATABASE_DRIVER=mysql" \
        --set "dashboard.env.DATABASE_DATASOURCE=$MYSQL_USER:$MYSQL_PASSWORD@tcp($MYSQL_HOST:$MYSQL_PORT)/$MYSQL_DATABASE?parseTime=true" \
        --set "dashboard.securityMode=false" \
        --set "dashboard.env.TTL_EVENT=336h" \
        --set "dashboard.env.TZ=Asia/Shanghai" \
        --set "dashboard.service.type=NodePort"
    echo "✓ Chaos Mesh 安装完成"
    echo ""
    echo "等待 Chaos Mesh 组件启动（最多 3 分钟）..."
    sleep 10
    if kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=chaos-dashboard -n "$NAMESPACE" --timeout=180s 2>/dev/null; then
        echo "✓ Chaos Mesh Dashboard 已启动"
    else
        echo "⚠ 警告: Chaos Mesh Dashboard 启动超时，请手动检查 pod 状态"
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=chaos-dashboard
    fi
fi
echo ""

# 设置固定的 NodePort 端口
echo "配置固定的 NodePort 端口..."
if kubectl get svc chaos-dashboard -n "$NAMESPACE" &>/dev/null; then
    # 检查 Service 类型
    CURRENT_TYPE=$(kubectl get svc chaos-dashboard -n "$NAMESPACE" -o jsonpath='{.spec.type}')
    if [ "$CURRENT_TYPE" != "NodePort" ]; then
        echo "将 Service 类型改为 NodePort..."
        kubectl patch svc chaos-dashboard -n "$NAMESPACE" -p '{"spec":{"type":"NodePort"}}'
    fi
    
    # 设置固定的 nodePort（HTTP 端口 2333）
    echo "设置 HTTP 端口 (2333) 的 NodePort 为 $DASHBOARD_NODEPORT_HTTP..."
    kubectl patch svc chaos-dashboard -n "$NAMESPACE" --type='json' \
        -p="[{\"op\": \"replace\", \"path\": \"/spec/ports/0/nodePort\", \"value\": $DASHBOARD_NODEPORT_HTTP}]" 2>/dev/null || \
    kubectl patch svc chaos-dashboard -n "$NAMESPACE" --type='json' \
        -p="[{\"op\": \"add\", \"path\": \"/spec/ports/0/nodePort\", \"value\": $DASHBOARD_NODEPORT_HTTP}]"
    
    # 设置固定的 nodePort（指标端口 2334）
    echo "设置指标端口 (2334) 的 NodePort 为 $DASHBOARD_NODEPORT_METRIC..."
    kubectl patch svc chaos-dashboard -n "$NAMESPACE" --type='json' \
        -p="[{\"op\": \"replace\", \"path\": \"/spec/ports/1/nodePort\", \"value\": $DASHBOARD_NODEPORT_METRIC}]" 2>/dev/null || \
    kubectl patch svc chaos-dashboard -n "$NAMESPACE" --type='json' \
        -p="[{\"op\": \"add\", \"path\": \"/spec/ports/1/nodePort\", \"value\": $DASHBOARD_NODEPORT_METRIC}]"
    
    echo "✓ NodePort 端口已设置为固定值"
else
    echo "⚠ 警告: 未找到 chaos-dashboard Service，跳过 NodePort 配置"
fi
echo ""

# 检查是否在正确的目录
if [ ! -f "$SCRIPT_DIR/mysql-secret.yaml" ]; then
    echo "错误: 请在包含 YAML 配置文件的目录中运行此脚本"
    exit 1
fi

echo "步骤 1/7: 创建 MySQL Secret..."
kubectl apply -f "$SCRIPT_DIR/mysql-secret.yaml"
echo "✓ MySQL Secret 已创建"
echo ""

echo "步骤 2/7: 创建 MySQL PVC..."
kubectl apply -f "$SCRIPT_DIR/mysql-pvc.yaml"
echo "✓ MySQL PVC 已创建"
echo ""

echo "步骤 3/7: 创建 MySQL ConfigMap..."
kubectl apply -f "$SCRIPT_DIR/mysql-configmap.yaml"
echo "✓ MySQL ConfigMap 已创建"
echo ""

echo "步骤 4/7: 创建 MySQL Deployment 和 Service..."
kubectl apply -f "$SCRIPT_DIR/mysql-deployment.yaml"
kubectl apply -f "$SCRIPT_DIR/mysql-service.yaml"
echo "✓ MySQL Deployment 和 Service 已创建"
echo ""

echo "步骤 5/7: 等待 MySQL 启动（最多 2 分钟）..."
if kubectl wait --for=condition=ready pod -l app=mysql -n "$NAMESPACE" --timeout=120s 2>/dev/null; then
    echo "✓ MySQL 已成功启动"
else
    echo "⚠ 警告: MySQL 启动超时，请手动检查 pod 状态"
    kubectl get pods -n "$NAMESPACE" -l app=mysql
fi
echo ""

echo "步骤 6/7: 更新 chaos-dashboard 配置..."
if kubectl get deployment chaos-dashboard -n "$NAMESPACE" &>/dev/null; then
    # 更新数据库连接为使用集群内的 MySQL 服务
    kubectl patch deployment chaos-dashboard -n "$NAMESPACE" --type='json' \
        -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env/1/value", "value": "root:elastic@tcp(mysql:3306)/chaos_mesh?parseTime=true"}]'
    echo "✓ chaos-dashboard 配置已更新为使用集群内 MySQL 服务"
    
    echo "等待 chaos-dashboard 重启（最多 2 分钟）..."
    sleep 5
    if kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=chaos-dashboard -n "$NAMESPACE" --timeout=120s 2>/dev/null; then
        echo "✓ chaos-dashboard 已成功重启"
    else
        echo "⚠ 警告: chaos-dashboard 重启超时，请手动检查 pod 状态"
        kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/component=chaos-dashboard
    fi
else
    echo "⚠ 警告: 未找到 chaos-dashboard deployment，跳过配置更新"
fi
echo ""

echo "步骤 7/7: 验证安装..."
echo ""
echo "=========================================="
echo "安装完成！"
echo "=========================================="
echo ""
echo "验证安装状态:"
kubectl get pods -n "$NAMESPACE" | grep -E "NAME|mysql|chaos-dashboard"
echo ""
echo "查看所有资源:"
kubectl get all -n "$NAMESPACE" | grep -E "mysql|chaos-dashboard"
echo ""
echo "测试 MySQL 连接:"
echo "kubectl run mysql-test --rm -i --restart=Never --image=mysql:8.0 --namespace=$NAMESPACE -- \\"
echo "  mysql -h mysql -uroot -pelastic -e 'SHOW DATABASES;'"
echo ""
echo "访问 Chaos Mesh Dashboard:"
echo "方式 1 - 使用 NodePort（固定端口）:"
echo "  通过任意节点 IP 访问: http://<节点IP>:$DASHBOARD_NODEPORT_HTTP"
echo "  指标端口: <节点IP>:$DASHBOARD_NODEPORT_METRIC"
echo ""
echo "方式 2 - 使用 port-forward:"
echo "  kubectl port-forward -n $NAMESPACE svc/chaos-dashboard 2333:2333"
echo "  然后在浏览器中访问: http://localhost:2333"

