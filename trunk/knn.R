con <- dbConnect(dbDriver("SQLite"), dbname = '~/repositories/prediggit/res_for_Jan09.db')
tr1 = dbGetQuery(con, "select id,time,attention,user,domain,topic,headline,description from features WHERE popular = '0' limit 1000")
tr2 = dbGetQuery(con, "select id,time,attention,user,domain,topic,headline,description from features WHERE popular = '1' limit 1000")
train = rbind(tr1,tr2)

te1 = dbGetQuery(con, "select id,time,attention,user,domain,topic,headline,description from features WHERE popular = '0' limit 1000,50")
te2 = dbGetQuery(con, "select id,time,attention,user,domain,topic,headline,description from features WHERE popular = '1' limit 1000,50")
test = rbind(te1,te2)

p1 = dbGetQuery(con, "select popular from features WHERE popular='0' limit 1000")
p2 = dbGetQuery(con, "select popular from features WHERE popular='1' limit 1000")
popular = rbind(p1,p2)

cl <- factor(c(rep("u", 1000), rep("p", 1000)))
knn(train, test, cl, k = 3, prob=TRUE)