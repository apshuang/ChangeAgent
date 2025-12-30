# MySQL 和 Chaos-Mesh 快速参考命令

## 快速安装（使用脚本）

```bash
cd /home/ubuntu/research
chmod +x setup-mysql-chaos-mesh.sh
./setup-mysql-chaos-mesh.sh
```

## 手动安装步骤

### 1. 创建所有 MySQL 资源

```bash
kubectl apply -f mysql-secret.yaml
kubectl apply -f mysql-pvc.yaml
kubectl apply -f mysql-configmap.yaml
kubectl apply -f mysql-deployment.yaml
kubectl apply -f mysql-service.yaml
```

### 2. 等待 MySQL 启动

```bash
kubectl wait --for=condition=ready pod -l app=mysql -n chaos-mesh --timeout=120s
```

### 3. 更新 chaos-dashboard 配置

```bash
kubectl patch deployment chaos-dashboard -n chaos-mesh --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env/1/value", "value": "root:elastic@tcp(mysql:3306)/chaos_mesh?parseTime=true"}]'
```

### 4. 验证安装

```bash
# 检查 pod 状态
kubectl get pods -n chaos-mesh | grep -E "mysql|chaos-dashboard"

# 测试 MySQL 连接
kubectl run mysql-test --rm -i --restart=Never --image=mysql:8.0 --namespace=chaos-mesh -- \
  mysql -h mysql -uroot -pelastic -e "SHOW DATABASES;"
```

## 常用检查命令

```bash
# 查看所有相关资源
kubectl get all -n chaos-mesh | grep -E "mysql|chaos-dashboard"

# 查看 MySQL pod 日志
kubectl logs -n chaos-mesh -l app=mysql --tail=50

# 查看 chaos-dashboard pod 日志
kubectl logs -n chaos-mesh -l app.kubernetes.io/component=chaos-dashboard --tail=50

# 检查 chaos-dashboard 配置
kubectl get deployment chaos-dashboard -n chaos-mesh -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="DATABASE_DATASOURCE")].value}'

# 连接到 MySQL
kubectl run mysql-client --rm -it --restart=Never --image=mysql:8.0 --namespace=chaos-mesh -- \
  mysql -h mysql -uroot -pelastic
```

## 清理命令

```bash
# 删除所有 MySQL 资源
kubectl delete deployment mysql -n chaos-mesh
kubectl delete service mysql -n chaos-mesh
kubectl delete pvc mysql-pvc -n chaos-mesh
kubectl delete secret mysql-secret -n chaos-mesh
kubectl delete configmap mysql-init -n chaos-mesh
```

