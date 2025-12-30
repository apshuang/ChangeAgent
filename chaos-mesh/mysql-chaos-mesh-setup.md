# MySQL 和 Chaos-Mesh 完整配置指南

本文档提供了在 Kubernetes 的 `chaos-mesh` 命名空间中安装 MySQL 并配置 chaos-dashboard 连接的完整步骤。

## 前置条件

- 已安装并配置好 Kubernetes 集群
- 已安装 kubectl 并具有集群访问权限
- chaos-mesh 命名空间已存在

## 一、创建 MySQL 资源

### 1.1 创建 MySQL Secret

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: chaos-mesh
type: Opaque
stringData:
  mysql-root-password: elastic
  mysql-password: elastic
  mysql-user: root
  mysql-database: chaos_mesh
EOF
```

或者使用文件：

```bash
kubectl apply -f mysql-secret.yaml
```

### 1.2 创建 MySQL PersistentVolumeClaim

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
  namespace: chaos-mesh
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
```

或者使用文件：

```bash
kubectl apply -f mysql-pvc.yaml
```

### 1.3 创建 MySQL 初始化 ConfigMap

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-init
  namespace: chaos-mesh
data:
  init.sql: |
    -- 允许 root 用户从任何主机连接
    CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'elastic';
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
EOF
```

或者使用文件：

```bash
kubectl apply -f mysql-configmap.yaml
```

### 1.4 创建 MySQL Deployment

```bash
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: chaos-mesh
  labels:
    app: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
          name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-database
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
        - name: mysql-init
          mountPath: /docker-entrypoint-initdb.d
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: mysql-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
      - name: mysql-init
        configMap:
          name: mysql-init
EOF
```

或者使用文件：

```bash
kubectl apply -f mysql-deployment.yaml
```

### 1.5 创建 MySQL Service

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: chaos-mesh
  labels:
    app: mysql
spec:
  type: ClusterIP
  ports:
  - port: 3306
    targetPort: 3306
    protocol: TCP
    name: mysql
  selector:
    app: mysql
EOF
```

或者使用文件：

```bash
kubectl apply -f mysql-service.yaml
```

## 二、等待 MySQL 启动

```bash
# 等待 MySQL pod 就绪（最多等待 2 分钟）
kubectl wait --for=condition=ready pod -l app=mysql -n chaos-mesh --timeout=120s

# 检查 MySQL pod 状态
kubectl get pods -n chaos-mesh -l app=mysql

# 验证 MySQL 连接（可选）
kubectl run mysql-test --rm -i --restart=Never --image=mysql:8.0 --namespace=chaos-mesh -- \
  mysql -h mysql -uroot -pelastic -e "SHOW DATABASES;"
```

## 三、更新 chaos-dashboard 配置

### 3.1 更新数据库连接地址

将 chaos-dashboard 的 `DATABASE_DATASOURCE` 环境变量从外部 IP 更新为 Kubernetes 服务名：

```bash
kubectl patch deployment chaos-dashboard -n chaos-mesh --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env/1/value", "value": "root:elastic@tcp(mysql:3306)/chaos_mesh?parseTime=true"}]'
```

### 3.2 验证配置更新

```bash
# 检查配置是否正确更新
kubectl get deployment chaos-dashboard -n chaos-mesh -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="DATABASE_DATASOURCE")].value}'

# 应该输出: root:elastic@tcp(mysql:3306)/chaos_mesh?parseTime=true
```

### 3.3 等待 chaos-dashboard 重启

```bash
# 检查 chaos-dashboard pod 状态
kubectl get pods -n chaos-mesh -l app.kubernetes.io/component=chaos-dashboard

# 等待 pod 就绪
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=chaos-dashboard -n chaos-mesh --timeout=120s
```

## 四、验证安装

### 4.1 检查所有资源状态

```bash
# 检查所有相关资源
kubectl get all -n chaos-mesh | grep -E "mysql|chaos-dashboard"

# 应该看到：
# - mysql pod: Running
# - chaos-dashboard pod: Running
# - mysql service: ClusterIP
# - chaos-dashboard service: NodePort
```

### 4.2 检查 MySQL 数据库

```bash
# 连接到 MySQL 并查看数据库
kubectl run mysql-client --rm -i --restart=Never --image=mysql:8.0 --namespace=chaos-mesh -- \
  mysql -h mysql -uroot -pelastic -e "SHOW DATABASES; SELECT User, Host FROM mysql.user WHERE User='root';"
```

### 4.3 检查 chaos-dashboard 日志

```bash
# 查看 chaos-dashboard 日志，确认没有数据库连接错误
kubectl logs -n chaos-mesh -l app.kubernetes.io/component=chaos-dashboard --tail=50
```

## 五、一键安装脚本

如果你想一次性执行所有步骤，可以使用以下脚本：

```bash
#!/bin/bash
set -e

NAMESPACE="chaos-mesh"

echo "创建 MySQL Secret..."
kubectl apply -f mysql-secret.yaml

echo "创建 MySQL PVC..."
kubectl apply -f mysql-pvc.yaml

echo "创建 MySQL ConfigMap..."
kubectl apply -f mysql-configmap.yaml

echo "创建 MySQL Deployment..."
kubectl apply -f mysql-deployment.yaml

echo "创建 MySQL Service..."
kubectl apply -f mysql-service.yaml

echo "等待 MySQL 启动..."
kubectl wait --for=condition=ready pod -l app=mysql -n $NAMESPACE --timeout=120s

echo "更新 chaos-dashboard 配置..."
kubectl patch deployment chaos-dashboard -n $NAMESPACE --type='json' \
  -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env/1/value", "value": "root:elastic@tcp(mysql:3306)/chaos_mesh?parseTime=true"}]'

echo "等待 chaos-dashboard 重启..."
sleep 10
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=chaos-dashboard -n $NAMESPACE --timeout=120s

echo "验证安装..."
kubectl get pods -n $NAMESPACE | grep -E "mysql|chaos-dashboard"

echo "安装完成！"
```

## 六、清理资源（如需要）

如果需要删除所有 MySQL 相关资源：

```bash
# 删除 MySQL 相关资源
kubectl delete deployment mysql -n chaos-mesh
kubectl delete service mysql -n chaos-mesh
kubectl delete pvc mysql-pvc -n chaos-mesh
kubectl delete secret mysql-secret -n chaos-mesh
kubectl delete configmap mysql-init -n chaos-mesh

# 恢复 chaos-dashboard 配置（如果需要）
# kubectl patch deployment chaos-dashboard -n chaos-mesh --type='json' \
#   -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env/1/value", "value": "root:elastic@tcp(10.10.1.202:3306)/chaos_mesh?parseTime=true"}]'
```

## 七、配置文件清单

所有配置文件应包含以下内容：

### mysql-secret.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: chaos-mesh
type: Opaque
stringData:
  mysql-root-password: elastic
  mysql-password: elastic
  mysql-user: root
  mysql-database: chaos_mesh
```

### mysql-pvc.yaml
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mysql-pvc
  namespace: chaos-mesh
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### mysql-configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mysql-init
  namespace: chaos-mesh
data:
  init.sql: |
    -- 允许 root 用户从任何主机连接
    CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'elastic';
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
```

### mysql-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: chaos-mesh
  labels:
    app: mysql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
          name: mysql
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-root-password
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: mysql-database
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
        - name: mysql-init
          mountPath: /docker-entrypoint-initdb.d
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      volumes:
      - name: mysql-storage
        persistentVolumeClaim:
          claimName: mysql-pvc
      - name: mysql-init
        configMap:
          name: mysql-init
```

### mysql-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: chaos-mesh
  labels:
    app: mysql
spec:
  type: ClusterIP
  ports:
  - port: 3306
    targetPort: 3306
    protocol: TCP
    name: mysql
  selector:
    app: mysql
```

## 八、常见问题排查

### 问题 1: MySQL pod 一直处于 CrashLoopBackOff

**原因**: 可能是配置错误，比如设置了 `MYSQL_USER=root`（MySQL 不允许）

**解决**: 确保 Deployment 中只设置 `MYSQL_ROOT_PASSWORD` 和 `MYSQL_DATABASE`，不要设置 `MYSQL_USER`

### 问题 2: 无法连接到 MySQL

**原因**: root 用户可能只允许从 localhost 连接

**解决**: 确保 ConfigMap 中的初始化脚本已正确执行，允许 root 从任何主机连接

### 问题 3: chaos-dashboard 仍然无法连接

**原因**: 配置未更新或 pod 未重启

**解决**: 
1. 检查配置是否正确更新
2. 删除旧的 pod 强制重启
3. 检查 MySQL 服务是否正常运行

## 九、配置说明

- **数据库地址**: `mysql:3306` (使用 Kubernetes 服务名，集群内部访问)
- **数据库名**: `chaos_mesh`
- **用户名**: `root`
- **密码**: `elastic`
- **存储**: 10Gi PersistentVolumeClaim
- **资源限制**: 内存 512Mi-1Gi, CPU 250m-500m

